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

from app.models.upload import UploadFile as UploadFileModel
from app.schemas.upload import UploadFileCreate

settings = get_settings()
blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_CONNECTION_STRING)
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}
ALLOWED_VIDEO_EXTENSION = {"mp4"}

class UploadFileService:
    def __init__(self):
        self.model = YOLO("app/model_weights/yolo11n.pt")  # โหลดโมเดล YOLO11s
        self.lp_model = YOLO("app/model_weights/license_platev1nbest.pt")
        self.names = self.model.names

        self.allowed_classes = [1, 2, 3, 5, 7]

    async def get_all_upload(self, session: AsyncSession):
        statement = select(UploadFileModel).order_by(desc(UploadFileModel.created_at))
       
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
    
        return JSONResponse({"file_name":file.filename,"upload_url":upload_url,"video_url": obj_detect_url, "upload_type": upload_type})
    '''
        # Save file information to database
        file_record = UploadFileCreate(
            upload_name=file.filename,
            upload_url=upload_url,
            obj_detect_url=obj_detect_url,
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

        return {"message": "File uploaded successfully", "filename": db_file.upload_name, "upload_url": db_file.upload_url, "Object_detectURL":obj_detect_url}
    '''

    async def get_upload(self, upload_id: str, session: AsyncSession):
        statement = select(UploadFileModel).where(UploadFileModel.id == upload_id)

        result = await session.execute(statement)

        file_upload = result.scalars().first()

        return file_upload if file_upload is not None else None

    async def delete_book(self,upload_id:str,session: AsyncSession):
        
        upload_to_delete = await self.get_upload(upload_id,session)

        if upload_to_delete is not None:
            await session.delete(upload_to_delete)

            await session.commit()

            return {}

        else:
            return None
    
    # service method

    async def _predict_image(self, file: UploadFile, container_client) -> str:
        _, ext = os.path.splitext(file.filename)
        ext = ext.lower() 

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_image:
            temp_image.write(await file.read())
            temp_image_path = temp_image.name
        
        original_blob_name = file.filename
        original_blob_client = container_client.get_blob_client(original_blob_name)
        
        with open(temp_image_path, "rb") as original_file:
            video_data_original = io.BytesIO(original_file.read())
            original_blob_client.upload_blob(video_data_original, overwrite=True, content_settings=ContentSettings(content_type='image/jpeg'))

        image = cv2.imread(temp_image_path)
        assert image is not None, "Error reading image file"

        results = self.model.predict(image, show=False)
        boxes = results[0].boxes.xyxy.cuda().tolist()
        clss = results[0].boxes.cls.cuda().tolist()
        annotator = Annotator(image, line_width=2, example=self.names)

        if boxes is not None:
            for box, cls in zip(boxes, clss):
                annotator.box_label(box, color=colors(int(cls), True), label=self.names[int(cls)])

        output_path = os.path.join(tempfile.gettempdir(), "processed_image.jpg")
        cv2.imwrite(output_path, image)


        blob_name = f"predicted_{file.filename}"
        blob_client = container_client.get_blob_client(blob_name)

        with open(output_path, "rb") as output_file:
            image_data_predicted = io.BytesIO(output_file.read())
            blob_client.upload_blob(image_data_predicted, overwrite=True, content_settings=ContentSettings(content_type='image/jpeg'))

        os.remove(temp_image_path)
        os.remove(output_path)

        image_url = f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net/{settings.AZURE_CONTAINER_NAME}/{blob_name}"
        return image_url
     

    async def _predict_video(self, file: UploadFile, container_client) -> str:
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
            annotator = Annotator(im0, line_width=2, example=self.names)

            # Draw bounding boxes only for allowed classes
            if boxes is not None:
                for box, cls in zip(boxes, clss):
                    if int(cls) in self.allowed_classes:
                        # Draw bounding box for allowed classes
                        annotator.box_label(box, color=colors(int(cls), True), label=self.names[int(cls)])

                        # Crop the vehicle area and run license plate detection
                        x1, y1, x2, y2 = map(int, box)
                        vehicle_crop = im0[y1:y2, x1:x2]

                        # Detect license plates within the vehicle area
                        lp_results = self.lp_model.predict(vehicle_crop, show=False)
                        lp_boxes = lp_results[0].boxes.xyxy.cpu().tolist()

                        # Annotate detected license plates on the original frame
                        if lp_boxes:  # Only proceed if license plates are detected
                            for lp_box in lp_boxes:
                                lp_x1, lp_y1, lp_x2, lp_y2 = map(int, lp_box)
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
                                "upload_id": 1,  # Fixed value as per your request
                                "crop_image_url": crop_image_url,
                                "crop_class_name": str(cls),  # Get class name from the detected class
                                "license_plate": "EN 2332",  # Fixed value as per your request
                                "crop_timestamp": crop_timestamp  # Current frame number
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
        return video_url