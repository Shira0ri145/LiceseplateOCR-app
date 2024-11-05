import io
import os
import tempfile
from typing import List
import cv2
from fastapi import HTTPException, status, UploadFile
from fastapi.responses import JSONResponse
import numpy as np
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from azure.storage.blob import BlobServiceClient, ContentSettings
from app.config.settings import get_settings
from ultralytics import YOLO 
from ultralytics.utils.plotting import Annotator, colors

from app.models.cropped_image import CroppedImage
from app.models.upload import UploadFile as UploadFileModel
from app.schemas.upload import UploadFileCreate

import easyocr

settings = get_settings()
blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_CONNECTION_STRING)
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}
ALLOWED_VIDEO_EXTENSION = {"mp4"}

class UploadFileService:
    def __init__(self):
        self.model = YOLO("app/model_weights/merq_vehicleV1m.pt")  # โหลดโมเดล YOLO11s
        self.lp_model = YOLO("app/model_weights/license_platev1nbest.pt")
        self.names = self.model.names

        self.ocr_reader = easyocr.Reader(['th'])

        # self.allowed_classes = [1, 2, 3, 5, 7]

    async def get_all_upload(self, session: AsyncSession):
        statement = select(UploadFileModel).order_by(desc(UploadFileModel.created_at))
       
        result = await session.execute(statement)
        
        return result.scalars().all()

    async def get_user_uploads(self, user_uid: str, session: AsyncSession):
        user_uid_int = int(user_uid)
        statement = (
            select(UploadFileModel)
            .where(UploadFileModel.user_id == user_uid_int)  # ใช้ user_uid ที่แปลงแล้ว
            .order_by(desc(UploadFileModel.created_at))
        )
        
        result = await session.execute(statement)
        return result.scalars().all()


    async def upload_file(
        self, 
        session: AsyncSession, 
        file: UploadFile, 
        user_id: int
    ) -> dict:
        container_client = blob_service_client.get_container_client(settings.AZURE_CONTAINER_NAME)

        # Check file type: image or video
        if file.content_type.startswith("image/"):
            ext = file.filename.split(".")[-1].lower()
            if ext not in ALLOWED_IMAGE_EXTENSIONS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid image format. Only jpg, jpeg, and png are allowed."
                )
            upload_type = "image"
            obj_detect_url = await self._predict_image(file, container_client)
            
        elif file.content_type.startswith("video/"):
            ext = file.filename.split(".")[-1].lower()
            if ext not in ALLOWED_VIDEO_EXTENSION:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid video format. Only mp4 is allowed."
                )
            upload_type = "video"
            obj_detect_url = await self._predict_video(file, container_client)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only images (jpg, jpeg, png) and videos (mp4) are allowed."
            )

        # checking all response
        upload_url = f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net/{settings.AZURE_CONTAINER_NAME}/{file.filename}"
        
        # return JSONResponse({"file_name":file.filename,"upload_url":upload_url,"video_url": obj_detect_url, "upload_type": upload_type})
        '''
        response_data = {
            "file_name":file.filename,
            "upload_url":upload_url,
            "video_url": obj_detect_url["predict_url"], 
            "upload_type": upload_type,
            "cropped_images": obj_detect_url["cropped_images"]
        }
        return JSONResponse(content=response_data)
        '''

        # Save file information to database
        file_record = UploadFileCreate(
            upload_name=file.filename,
            upload_url=upload_url,
            obj_detect_url=obj_detect_url["predict_url"],
            upload_type=upload_type
        )
        db_file = UploadFileModel(
            user_id=user_id,
            upload_name=file_record.upload_name,
            upload_url=file_record.upload_url,
            obj_detect_url=file_record.obj_detect_url,
            upload_type=file_record.upload_type
        )
        session.add(db_file)
        await session.commit()
        await session.refresh(db_file)

        # Insert cropped images into the database and collect their data
        cropped_images_data = []
        for cropped in obj_detect_url["cropped_images"]:
            new_cropped_image = CroppedImage(
                upload_id=db_file.id,  # Use the ID from the uploaded file
                crop_image_url=cropped["crop_image_url"],
                crop_class_name=cropped["crop_class_name"],
                license_plate=cropped["license_plate"],
                crop_timestamp=round(cropped["crop_timestamp"], 2)  # ปัดให้เป็น 2 ตำแหน่งทศนิยม
            )
            session.add(new_cropped_image)

        await session.commit() 

        all_cropped_images = await session.execute(
            select(CroppedImage).where(CroppedImage.upload_id == db_file.id)
        )
        cropped_images_data = all_cropped_images.scalars().all()

        response_data = [
        {
            "id": cropped_image.id,
            "upload_id": cropped_image.upload_id,
            "crop_image_url": cropped_image.crop_image_url,
            "crop_class_name": cropped_image.crop_class_name,
            "license_plate": cropped_image.license_plate,
            "crop_timestamp": cropped_image.crop_timestamp
        } for cropped_image in cropped_images_data
        ]

        return {
            "message": "File uploaded successfully", 
            "filename": db_file.upload_name, 
            "upload_url": db_file.upload_url, 
            "detect_url": obj_detect_url["predict_url"],
            "cropped_images": response_data  # Include the cropped images data in the response
        }
    

    async def get_upload(self, upload_id: str, session: AsyncSession):
        statement = select(UploadFileModel).where(UploadFileModel.id == upload_id)

        result = await session.execute(statement)

        file_upload = result.scalars().first()

        return file_upload if file_upload is not None else None

    async def delete_file(self,upload_id:str,session: AsyncSession):
        
        upload_to_delete = await self.get_upload(upload_id,session)

        if upload_to_delete is not None:
            await session.delete(upload_to_delete)

            await session.commit()

            return {}

        else:
            return None
    
    # service method
    async def _predict_image(self, file: UploadFile, container_client) -> dict:
        _, ext = os.path.splitext(file.filename)
        ext = ext.lower()

        # Create a temporary file for the uploaded image
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_image:
            temp_image.write(await file.read())
            temp_image_path = temp_image.name

        original_blob_name = file.filename
        original_blob_client = container_client.get_blob_client(original_blob_name)

        # Upload original image
        with open(temp_image_path, "rb") as original_file:
            image_data_original = io.BytesIO(original_file.read())
            original_blob_client.upload_blob(image_data_original, overwrite=True, content_settings=ContentSettings(content_type='image/jpeg'))

        # Read image and set up for output
        image = cv2.imread(temp_image_path)
        assert image is not None, "Error reading image file"
        output_path = os.path.join(tempfile.gettempdir(), "processed_image.jpg")

        # Detect objects in the image
        results = self.model.predict(image, show=False)
        boxes = results[0].boxes.xyxy.cpu().tolist()
        clss = results[0].boxes.cls.cpu().tolist()
        confs = results[0].boxes.conf.cpu().tolist()  # Confidence scores
        annotator = Annotator(image, line_width=2, example=self.names)

        cropped_images = []

        # Draw bounding boxes and crop detected vehicles
        if boxes is not None:
            for box, cls, conf in zip(boxes, clss, confs):
                if conf >= 0.6:
                    # Annotate the detected object
                    annotator.box_label(box, label=self.names[int(cls)], color=colors(int(cls), True))

                    # Crop the vehicle area and run license plate detection
                    x1, y1, x2, y2 = map(int, box)
                    vehicle_crop = image[y1:y2, x1:x2]

                    # Detect license plates within the vehicle area
                    lp_results = self.lp_model.predict(vehicle_crop, show=False)
                    lp_boxes = lp_results[0].boxes.xyxy.cpu().tolist()

                    # If confidence is high enough, process the cropped image
                    if conf >= 0.6:
                        # Annotate detected license plates on the original image
                        if lp_boxes:  # Only proceed if license plates are detected
                            for lp_box in lp_boxes:
                                
                                lp_x1, lp_y1, lp_x2, lp_y2 = map(int, lp_box)

                                lp_crop = vehicle_crop[lp_y1:lp_y2, lp_x1:lp_x2]

                                # BG to Gray and enhance image
                                lp_crop_gray = cv2.cvtColor(lp_crop, cv2.COLOR_BGR2GRAY)
                                
                                 # Perform OCR on the license plate crop
                                # detections = self.ocr_reader.readtext(lp_crop_thresh)
                                ocr_result = self.ocr_reader.readtext(lp_crop_gray)
                                if len(ocr_result) >= 2:
                                    combined_license_plate_text = " ".join(item[1] for item in ocr_result[:2])
                                else:
                                    combined_license_plate_text = " ".join(item[1] for item in ocr_result)
                                

                                annotator.box_label(
                                    (x1 + lp_x1, y1 + lp_y1, x1 + lp_x2, y1 + lp_y2),
                                    color=(0, 255, 0),
                                    label = "license plate"
                                )

                            # Save cropped vehicle image to Azure Blob if license plates are detected
                            crop_image = image[y1:y2, x1:x2]

                            crop_folder_name = f"crop_{file.filename}"
                            crop_image_filename = f"{crop_folder_name}/crop_{file.filename}_{len(cropped_images) + 1}.jpg"

                            # Upload the cropped image to Azure Blob Storage
                            crop_blob_client = container_client.get_blob_client(crop_image_filename)
                            _, buffer = cv2.imencode('.jpg', crop_image)  # Encode image to JPEG format
                            crop_blob_client.upload_blob(io.BytesIO(buffer), overwrite=True, content_settings=ContentSettings(content_type='image/jpeg'))

                            # Create the URL for the cropped image
                            crop_image_url = f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net/{settings.AZURE_CONTAINER_NAME}/{crop_image_filename}"

                            # Add the cropped image data to the array
                            cropped_images.append({
                                "crop_image_url": crop_image_url,
                                "crop_class_name": self.names[int(cls)],  # Get class name from the detected class
                                "license_plate": combined_license_plate_text,  # Fixed value as per your request
                                "crop_timestamp": 0  # Placeholder timestamp
                            })

        # Write processed image to output
        cv2.imwrite(output_path, image)
        blob_name = f"predicted_{file.filename}"
        blob_client = container_client.get_blob_client(blob_name)

        with open(output_path, "rb") as output_file:
            image_data_predicted = io.BytesIO(output_file.read())
            blob_client.upload_blob(image_data_predicted, overwrite=True, content_settings=ContentSettings(content_type='image/jpeg'))

        # Clean up temporary files
        os.remove(temp_image_path)
        os.remove(output_path)

        # Return URL of the uploaded image and cropped images
        image_url = f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net/{settings.AZURE_CONTAINER_NAME}/{blob_name}"
        return {
            "predict_url": image_url,
            "cropped_images": cropped_images
        }


    async def _predict_video(self, file: UploadFile, container_client) -> dict:
        # Create a temporary file for the uploaded video
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
            temp_video.write(await file.read())
            temp_video_path = temp_video.name

        original_blob_name = file.filename
        original_blob_client = container_client.get_blob_client(original_blob_name)
        
        # Upload original video
        with open(temp_video_path, "rb") as original_file:
            video_data_original = io.BytesIO(original_file.read())
            original_blob_client.upload_blob(video_data_original, overwrite=True, content_settings=ContentSettings(content_type='video/mp4'))

        # Read video and set up for output
        cap = cv2.VideoCapture(temp_video_path)
        assert cap.isOpened(), "Error reading video file"
        output_path = os.path.join(tempfile.gettempdir(), "processed_video.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        cropped_images = []
        # Process each frame
        while cap.isOpened():
            success, im0 = cap.read()
            if not success:
                break

            # Detect objects in the frame
            results = self.model.predict(im0, show=False)
            boxes = results[0].boxes.xyxy.cpu().tolist()
            clss = results[0].boxes.cls.cpu().tolist()
            confs = results[0].boxes.conf.cpu().tolist()
            annotator = Annotator(im0, line_width=2, example=self.names)

            # Draw bounding boxes only for allowed classes
            if boxes is not None:
                for box, cls, conf in zip(boxes, clss, confs):
                    if conf >= 0.6:
                        # annotator.box_label(box, color=colors(int(cls), True), label=self.names[int(cls)])
                        annotator.box_label(box, label=self.names[int(cls)], color=colors(int(cls), True))

                    
                        # Crop the vehicle area and run license plate detection
                        x1, y1, x2, y2 = map(int, box)
                        vehicle_crop = im0[y1:y2, x1:x2]

                        # Detect license plates within the vehicle area
                        lp_results = self.lp_model.predict(vehicle_crop, show=False)
                        lp_boxes = lp_results[0].boxes.xyxy.cpu().tolist()

                        if conf >= 0.75:
                            # Annotate detected license plates on the original frame
                            if lp_boxes:  # Only proceed if license plates are detected
                                for lp_box in lp_boxes:
                                    lp_x1, lp_y1, lp_x2, lp_y2 = map(int, lp_box)

                                    lp_crop = vehicle_crop[lp_y1:lp_y2, lp_x1:lp_x2]
                                    lp_crop_gray = cv2.cvtColor(lp_crop, cv2.COLOR_BGR2GRAY)

                                    # Perform OCR on the license plate crop
                                    # detections = self.ocr_reader.readtext(lp_crop_thresh)
                                    ocr_result = self.ocr_reader.readtext(lp_crop_gray)
                                    if len(ocr_result) >= 2:
                                        combined_license_plate_text = " ".join(item[1] for item in ocr_result[:2])
                                    else:
                                        combined_license_plate_text = " ".join(item[1] for item in ocr_result)

                                    annotator.box_label(
                                        (x1 + lp_x1, y1 + lp_y1, x1 + lp_x2, y1 + lp_y2),
                                        color=(0, 255, 0),
                                        label="License Plate"
                                    )


                                    # Save cropped vehicle image to Azure Blob if license plates are detected
                                    crop_image = im0[y1:y2, x1:x2]

                                    crop_folder_name = f"crop_{file.filename}"
                                    crop_image_filename = f"{crop_folder_name}/crop_{file.filename}_{len(cropped_images) + 1}.jpg"  # Generate a unique filename

                                    # Upload the cropped image to Azure Blob Storage
                                    crop_blob_client = container_client.get_blob_client(crop_image_filename)
                                    _, buffer = cv2.imencode('.jpg', crop_image)  # Encode image to JPEG format
                                    crop_blob_client.upload_blob(io.BytesIO(buffer), overwrite=True, content_settings=ContentSettings(content_type='image/jpeg'))

                                    # Create the URL for the cropped image
                                    crop_image_url = f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net/{settings.AZURE_CONTAINER_NAME}/{crop_image_filename}"

                                    # Add the cropped image data to the array
                                    current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                                    crop_timestamp = current_frame / fps
                                    cropped_images.append({
                                        "crop_image_url": crop_image_url,
                                        "crop_class_name": self.names[int(cls)],  # Get class name from the detected class
                                        "license_plate": combined_license_plate_text,  # Extracted license plate text
                                        "crop_timestamp": round(crop_timestamp, 2)  # Current frame number
                                    })

            # Write processed frame to output
            out.write(im0)

        # Release resources
        cap.release()
        out.release()

        # Upload processed video
        blob_name = f"predicted_{file.filename}"
        blob_client = container_client.get_blob_client(blob_name)
        with open(output_path, "rb") as output_file:
            video_data_predicted = io.BytesIO(output_file.read())
            blob_client.upload_blob(video_data_predicted, overwrite=True, content_settings=ContentSettings(content_type='video/mp4'))

        # Clean up temporary files
        os.remove(temp_video_path)
        os.remove(output_path)

        # Return URL of the uploaded video
        video_url = f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net/{settings.AZURE_CONTAINER_NAME}/{blob_name}"
        return {
            "predict_url": video_url,
            "cropped_images": cropped_images
        }
    
