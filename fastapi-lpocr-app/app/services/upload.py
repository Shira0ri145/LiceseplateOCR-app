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
ALLOWED_VIDEO_MIME = "video/"

class UploadFileService:
    def __init__(self):
        self.model = YOLO("app/model_weights/yolo11s.pt")  # โหลดโมเดล YOLO11s
        self.names = self.model.names

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
            # obj_detect_url = await self._predict_image(file, container_client)
            
        elif file.content_type.startswith(ALLOWED_VIDEO_MIME):
            upload_type = "video"
            upload_url = await self.upload_defaultfile(file, container_client)

            obj_detect_url = await self._predict_video(file, container_client)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only images (jpg, jpeg, png) and videos are allowed."
            )


        # checking all response
        upload_url = f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net/{settings.AZURE_CONTAINER_NAME}/{file.filename}"

        # return JSONResponse({"file_name":file.filename,"upload_url":upload_url,"video_url": obj_detect_url, "upload_type": upload_type})
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
    async def upload_defaultfile(self, file: UploadFile, container_client) -> str:
    # Upload file to Azure Blob Storage
        # defaultfile_blob_client = container_client.get_blob_client(file.filename)

        # Read the file content and upload it
        pass
        
        # upload_url = f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net/{settings.AZURE_CONTAINER_NAME}/{file.filename}"
        # return upload_url

    async def _predict_image(self, file: UploadFile, container_client) -> str:

            '''input_image = await file.read()'''

            # Object Detection
            '''input_image = cv2.imdecode(np.frombuffer(input_image, np.uint8), cv2.IMREAD_COLOR)
            results = self.model(input_image)'''
            

            return "https://www.example.com/"
            
            
            '''cv2.imwrite(output_image_path, detected_image)

            # Upload to Azure Blob Storage
            detected_blob_client = container_client.get_blob_client(f"detected_{file.filename}")
            with open(output_image_path, "rb") as detected_image_file:
                detected_blob_client.upload_blob(detected_image_file, overwrite=True)

            return f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net/{settings.AZURE_CONTAINER_NAME}/detected_{file.filename}"'''

    async def _predict_video(self, file: UploadFile, container_client) -> str:
        
        # สร้างไฟล์ชั่วคราวสำหรับเก็บข้อมูลวิดีโอที่อัปโหลด
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
            temp_video.write(await file.read())
            temp_video_path = temp_video.name

        original_blob_name = file.filename
        original_blob_client = container_client.get_blob_client(original_blob_name)
        
        # อ่านข้อมูลวิดีโอจากไฟล์ชั่วคราวและอัปโหลด
        with open(temp_video_path, "rb") as original_file:
            video_data_original = io.BytesIO(original_file.read())
            original_blob_client.upload_blob(video_data_original, overwrite=True, content_settings=ContentSettings(content_type='video/mp4'))

        # อ่านข้อมูลวิดีโอจากไฟล์ที่อัปโหลด
        cap = cv2.VideoCapture(temp_video_path)
        assert cap.isOpened(), "Error reading video file"

        # กำหนดชื่อไฟล์เอาท์พุต
        output_path = os.path.join(tempfile.gettempdir(), "processed_video.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        # ประมวลผลวิดีโอทีละเฟรม
        while cap.isOpened():
            success, im0 = cap.read()
            if not success:
                break

            # ตรวจจับวัตถุในแต่ละเฟรม
            results = self.model.predict(im0, show=False)
            boxes = results[0].boxes.xyxy.cuda().tolist()
            clss = results[0].boxes.cls.cuda().tolist()
            annotator = Annotator(im0, line_width=2, example=self.names)

            # วาดกรอบรอบวัตถุที่ตรวจจับได้
            if boxes is not None:
                for box, cls in zip(boxes, clss):
                    annotator.box_label(box, color=colors(int(cls), True), label=self.names[int(cls)])

            # เขียนเฟรมที่ประมวลผลแล้วไปยังวิดีโอเอาท์พุต
            out.write(im0)

        # ปิดการเปิดวิดีโอและบันทึกวิดีโอ
        cap.release()
        out.release()
        '''
        original_blob_name = file.filename
        original_blob_client = container_client.get_blob_client(original_blob_name)
        video_data_original =  io.BytesIO(await file.read())
        original_blob_client.upload_blob(video_data_original, overwrite=True, content_settings=ContentSettings(content_type='video/mp4'))
        '''

        # upload predicted to Azure Blob Storage
        blob_name = f"predicted_{file.filename}"
        blob_client = container_client.get_blob_client(blob_name)

        with open(output_path, "rb") as output_file:
            video_data_predicted = io.BytesIO(output_file.read())
            blob_client.upload_blob(video_data_predicted, overwrite=True, content_settings=ContentSettings(content_type='video/mp4'))

        # ลบไฟล์ชั่วคราว
        os.remove(temp_video_path)
        os.remove(output_path)

        # ส่งคืน URL ของวิดีโอที่อัปโหลด
        video_url = f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net/{settings.AZURE_CONTAINER_NAME}/{blob_name}"
        return video_url

 