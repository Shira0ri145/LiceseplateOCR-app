from typing import List
from fastapi import APIRouter, Depends, File, status, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from app.config.database import db_dependency
from app.config.dependencies import AccessTokenBearer, RoleChecker, get_current_user
from app.config.settings import get_settings
from app.models.upload import UploadFile as UploadFileModel
from app.schemas.upload import UploadFileCreate
from azure.storage.blob import BlobServiceClient


# Create a new APIRouter instance for vehicle-related routes
vehicle_router = APIRouter(
    prefix='/vehicle',
    tags=['Vehicle']
)
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(["admin", "member"]))
settings = get_settings()

@vehicle_router.get('/', dependencies=[role_checker])
async def hello(vehicle_details=Depends(access_token_bearer)):
    return {"message": "Welcome to the vehicle page"}

ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}
ALLOWED_VIDEO_MIME = "video/"

@vehicle_router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_vehicle_file(
    db: db_dependency,
    file: UploadFile = File(...),
    token_details: dict = Depends(access_token_bearer),
) -> dict:
    user_id = int(token_details.get("user")["user_uid"])
    # print("Token Details:", token_details)


    # Initialize BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_CONNECTION_STRING)
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
    db.add(db_file)
    await db.commit()
    await db.refresh(db_file)

    return JSONResponse(content={"message": "File uploaded successfully", "filename": db_file.upload_name})


'''
@vehicle_router.get("/uploads", response_model=List[UploadFileResponse])
async def user_uploads_route(db: db_dependency,current_user=Depends(get_current_user)):
    user_id = current_user.id  # Assuming current_user has an id attribute
    try:
        uploads = await get_user_uploads(db, user_id)
        return uploads
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@vehicle_router.get("/all_uploads", response_model=List[UploadFileResponse], dependencies=[role_checker])
async def all_uploads_route(db: db_dependency):
    try:
        uploads = await get_all_uploads(db)
        return uploads
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''