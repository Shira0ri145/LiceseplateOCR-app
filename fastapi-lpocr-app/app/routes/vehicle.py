import select
from typing import List
from fastapi import APIRouter, Depends, File, status, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from app.config.database import db_dependency
from app.config.dependencies import AccessTokenBearer, RoleChecker, get_current_user
from app.config.settings import get_settings

from app.schemas.upload import UploadFileSchema
from app.services.upload import UploadFileService


# Create a new APIRouter instance for vehicle-related routes
vehicle_router = APIRouter(
    prefix='/api/vehicle',
    tags=['Vehicle']
)
access_token_bearer = AccessTokenBearer()
upload_service = UploadFileService()
role_checker = Depends(RoleChecker(["admin", "member"]))
admin_only = Depends(RoleChecker(["admin"]))
settings = get_settings()

@vehicle_router.get('/', dependencies=[role_checker])
async def hello(_: dict = Depends(access_token_bearer)):
    return {"message": "Welcome to the vehicle page"}

@vehicle_router.get("/uploads", response_model=List[UploadFileSchema], dependencies=[admin_only])
async def get_all_upload(db: db_dependency, _: dict = Depends(access_token_bearer)):
    file_upload = await upload_service.get_all_upload(db)
    return file_upload

@vehicle_router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_vehicle_file(
    db: db_dependency,
    file: UploadFile = File(...),
    token_details: dict = Depends(access_token_bearer),
) -> dict:
    user_id = int(token_details.get("user")["user_uid"])
    response = await upload_service.upload_file(db, file, user_id)
    return response

@vehicle_router.get("/{upload_id}")
async def get_vehicle_file(upload_id: int, db: db_dependency): 
    fileupload = await upload_service.get_upload(upload_id, db)

    if fileupload:
        return fileupload
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fileupload not found")


@vehicle_router.delete("/delete/{upload_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_upload(upload_id: int, db: db_dependency):
    fileupload_to_delete = await upload_service.delete_book(upload_id, db)

    # เดี๋ยวจะต้องมาลบรูปทีหลังด้วย เขียนกันลืมไว้ก่อน
    if fileupload_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fileupload not found")
    return {}

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