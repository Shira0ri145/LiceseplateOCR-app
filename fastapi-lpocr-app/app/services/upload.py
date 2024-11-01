import io
import os
import tempfile
from typing import List
import cv2
from fastapi import HTTPException, status, UploadFile
import numpy as np
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from azure.storage.blob import BlobServiceClient
from app.config.settings import get_settings
from ultralytics import YOLO 

from app.models.upload import UploadFile as UploadFileModel
from app.schemas.upload import UploadFileCreate

settings = get_settings()
blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_CONNECTION_STRING)
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}
ALLOWED_VIDEO_MIME = "video/"

class UploadFileService:
    def __init__(self):
        self.model = YOLO("app/model_weights/yolo11s.pt")  # โหลดโมเดล YOLO11s

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
            
        elif file.content_type.startswith(ALLOWED_VIDEO_MIME):
            upload_type = "video"
            obj_detect_url = await self._predict_video(file, container_client)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only images (jpg, jpeg, png) and videos are allowed."
            )

        # Upload file to Azure Blob Storage
        blob_client = container_client.get_blob_client(file.filename)
        blob_client.upload_blob(file.file, overwrite=True)

        # Get file URL from Azure Blob Storage
        upload_url = f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net/{settings.AZURE_CONTAINER_NAME}/{file.filename}"

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

        return {"message": "File uploaded successfully", "filename": db_file.upload_name}

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
        # setup temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            input_video_path = os.path.join(temp_dir, file.filename)
            output_video_path = os.path.join(temp_dir, f"detected_{file.filename}")
        
            with open(input_video_path, "wb") as temp_file:
                temp_file.write(file.read())

            # Object Detection
            video_capture = cv2.VideoCapture(input_video_path)
            frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(video_capture.get(cv2.CAP_PROP_FPS))

            # ตั้งค่าการบันทึกวิดีโอที่ตรวจจับแล้ว
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

            while video_capture.isOpened():
                ret, frame = video_capture.read()
                if not ret:
                    break
                results = self.model(frame)  # ทำ object detection กับแต่ละเฟรม
                detected_frame = results.render()[0]  # รูปภาพที่ผ่านการตรวจจับแล้ว
                out.write(detected_frame)  # เขียนเฟรมที่ตรวจจับแล้วลงไปในวิดีโอใหม่

            video_capture.release()
            out.release()

            # Upload to Azure Blob Storage
            detected_blob_client = container_client.get_blob_client(f"detected_{file.filename}")
            with open(output_video_path, "rb") as detected_video:
                detected_blob_client.upload_blob(detected_video, overwrite=True)

            return f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net/{settings.AZURE_CONTAINER_NAME}/detected_{file.filename}"

   