from fastapi import HTTPException
from azure.storage.blob import BlobServiceClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.upload import UploadFile as UploadFileModel
from app.schemas.upload import UploadFileCreate
from app.config.settings import get_settings
from datetime import datetime

settings = get_settings()
blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_CONNECTION_STRING)

async def upload_vehicle_file(db: AsyncSession, file: UploadFileCreate, user_id: int):
    # Check if the uploaded file is a video or image
    if file.upload_type.startswith('image/'):
        if not (file.upload_name.lower().endswith('.jpg') or file.upload_name.lower().endswith('.jpeg') or file.upload_name.lower().endswith('.png')):
            raise HTTPException(status_code=400, detail="Invalid image format. Only .jpg and .png are allowed.")
    elif not file.upload_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only images (jpg, png) and videos are allowed.")

    try:
        blob_client = blob_service_client.get_blob_client(container=settings.AZURE_CONTAINER_NAME, blob=file.upload_name)
        blob_client.upload_blob(file.file, overwrite=True)

        uploaded_file_url = f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net/{settings.AZURE_CONTAINER_NAME}/{file.upload_name}"

        new_upload = UploadFileModel(
            user_id=user_id,
            upload_name=file.upload_name,
            upload_url=uploaded_file_url,
            upload_type=file.upload_type,
            created_at=datetime.now()
        )

        db.add(new_upload)
        await db.commit()

        return uploaded_file_url

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_all_uploads(db: AsyncSession):
    uploads = await db.execute(select(UploadFileModel))
    return uploads.scalars().all()

async def get_user_uploads(db: AsyncSession, user_id: int):
    uploads = await db.execute(select(UploadFileModel).where(UploadFileModel.user_id == user_id))
    return uploads.scalars().all()

