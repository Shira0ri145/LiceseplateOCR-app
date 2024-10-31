from typing import List
from fastapi import HTTPException, status, UploadFile
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from azure.storage.blob import BlobServiceClient
from app.config.settings import get_settings

from app.models.upload import UploadFile as UploadFileModel
from app.schemas.upload import UploadFileCreate

settings = get_settings()
blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_CONNECTION_STRING)
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}
ALLOWED_VIDEO_MIME = "video/"

class UploadFileService:
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
        elif file.content_type.startswith(ALLOWED_VIDEO_MIME):
            upload_type = "video"
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
            upload_type=upload_type
        )
        db_file = UploadFileModel(
            user_id=user_id,
            upload_name=file_record.upload_name,
            upload_url=file_record.upload_url,
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
    

   