from typing import List
from fastapi import APIRouter, Depends, File, status, HTTPException, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from ultralytics import YOLO
from app.config.database import db_dependency
from app.config.dependencies import AccessTokenBearer, RoleChecker, get_current_user
from app.config.settings import get_settings

from azure.storage.blob import BlobServiceClient

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

blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_CONNECTION_STRING)

@vehicle_router.delete('/del_all_blob' , dependencies=[role_checker])
async def delete_all_blobs(container_name: str, _: dict = Depends(access_token_bearer)):
    try:
        # รับ client สำหรับ container ที่ระบุ
        container_client = blob_service_client.get_container_client(container_name)
        
        # ลบทุก blob ใน container
        blob_list = container_client.list_blobs()
        
        for blob in blob_list:
            blob_client = container_client.get_blob_client(blob.name)
            blob_client.delete_blob()
        
        return {"message": f"All blobs in container '{container_name}' have been deleted."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

@vehicle_router.get(
    "/user/uploads", response_model=List[UploadFileSchema], dependencies=[Depends(access_token_bearer)]
)
async def get_user_uploads(
    db: db_dependency,
    user_and_role: tuple = Depends(get_current_user),
):
    user, role = user_and_role  # ดึง user จาก get_current_user
    uploads = await upload_service.get_user_uploads(user.id, db)  # ใช้ user.id แทน user_uid
    if uploads is None:
        raise HTTPException(status_code=404, detail="No uploads found for this user.")
    return uploads

@vehicle_router.delete("/delete/{upload_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_upload(upload_id: int, db: db_dependency):
    fileupload_to_delete = await upload_service.delete_file(upload_id, db)

    # เดี๋ยวจะต้องมาลบรูปทีหลังด้วย เขียนกันลืมไว้ก่อน
    if fileupload_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fileupload not found")
    return {}
'''
import easyocr
ocr = easyocr.Reader(['th'])
from fastapi import Request

@vehicle_router.post("/ocr_form")
async def do_ocr_form(request: Request, file: UploadFile = File(...)):
    if file is not None:
        res = ocr.readtext(file.file.read())
        # รวมข้อความในลิสต์เป็นสตริงเดียวโดยใช้ join
        combined_text = " ".join(item[1] for item in res)
        return combined_text

    return {"error": "missing file"}'''
