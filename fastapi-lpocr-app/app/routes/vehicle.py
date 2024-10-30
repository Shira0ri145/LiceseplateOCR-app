from typing import List
from fastapi import APIRouter, Depends, File, status, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from app.config.database import db_dependency
from app.config.dependencies import AccessTokenBearer, RoleChecker, get_current_user
from app.models.upload import UploadFile as UploadFileModel
from app.schemas.upload import UploadFileCreate


# Create a new APIRouter instance for vehicle-related routes
vehicle_router = APIRouter(
    prefix='/vehicle',
    tags=['Vehicle']
)
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(["admin", "member"]))

@vehicle_router.get('/', dependencies=[role_checker])
async def hello(vehicle_details=Depends(access_token_bearer)):
    return {"message": "Welcome to the vehicle page"}



ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}
ALLOWED_VIDEO_MIME = "video/"

@vehicle_router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_vehicle_file(
    db: db_dependency,
    file: UploadFile = File(...),
    current_user=Depends(access_token_bearer)  # Retrieve user from token
):
    # Check file type: image or video
    if file.content_type.startswith("image/"):
        # Verify image format
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

    # Prepare file data for the database
    file_record = UploadFileCreate(
    upload_name=file.filename,
    upload_url=f"uploads/{file.filename}",  # Adjust the upload path as needed
    upload_type=upload_type
)

    # Save to database
    db_file = UploadFileModel(
        # user_id=current_user["id"],  # Access id from dictionary
        user_id=1,
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