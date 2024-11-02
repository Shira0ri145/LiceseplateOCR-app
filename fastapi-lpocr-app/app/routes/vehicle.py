from typing import List
from fastapi import APIRouter, Depends, File, status, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from ultralytics import YOLO
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

model = YOLO("app/model_weights/yolo11s.pt")
import numpy as np
from PIL import Image
import tempfile
import io
import cv2
import os
import shutil
from ultralytics.utils.plotting import Annotator, colors
from azure.storage.blob import BlobServiceClient,ContentSettings
names = model.names

@vehicle_router.post("/predict/")
async def predict(file: UploadFile = File(...)):
    # อ่านไฟล์ภาพจาก UploadFile
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    
    # แปลงภาพเป็น numpy array
    img_np = np.array(image)
    
    # ทำการ Predict โดยใช้ YOLO
    results = model(img_np)
    
    # วาดผลลัพธ์บนภาพ
    result_image = results[0].plot()
    
    # แปลงกลับเป็นภาพ PIL
    result_pil_image = Image.fromarray(result_image)

    # สร้าง byte stream ของภาพเพื่อส่งกลับไปยัง client
    byte_io = io.BytesIO()
    result_pil_image.save(byte_io, format='PNG')
    byte_io.seek(0)

    # ส่งภาพกลับไปเป็น response
    return StreamingResponse(byte_io, media_type="image/png")


'''
@vehicle_router.post("/predict-video/")
async def predict_video(file: UploadFile = File(...)):
    # สร้างไฟล์ชั่วคราวเพื่อเก็บวิดีโอ
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(await file.read())
        temp_video_path = temp_video.name

    # เปิดไฟล์วิดีโอ
    cap = cv2.VideoCapture(temp_video_path)
    assert cap.isOpened(), "Error reading video file"

    # สร้างวิดีโอเอาท์พุต
    output_path = "asdqoutput_video.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_path, fourcc, 30.0, (width, height))

    while cap.isOpened():
        success, im0 = cap.read()
        if not success:
            break

        # ทำการตรวจจับวัตถุ
        results = model.predict(im0, show=False)
        boxes = results[0].boxes.xyxy.cuda().tolist()
        clss = results[0].boxes.cls.cuda().tolist()
        annotator = Annotator(im0, line_width=2, example=names)

        # วาดกรอบรอบวัตถุที่ตรวจจับได้
        if boxes is not None:
            for box, cls in zip(boxes, clss):
                annotator.box_label(box, color=colors(int(cls), True), label=names[int(cls)])

        # เขียนเฟรมที่ประมวลผลแล้วไปยังวิดีโอใหม่
        out.write(im0)

    # ปิดการเปิดวิดีโอ
    cap.release()
    out.release()

    # อัปโหลดวิดีโอที่ประมวลผลแล้วไปยัง Azure Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(settings.AZURE_CONTAINER_NAME)
    
    # กำหนดชื่อไฟล์ใน Blob Storage
    blob_name = "processed_video.mp4"
    blob_client = container_client.get_blob_client(blob_name)

    with open(output_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True,content_settings=ContentSettings(content_type='video/mp4'))

    # ลบไฟล์ชั่วคราว
    # os.remove(temp_video_path)
    # os.remove(output_path)

    # ส่งคืน URL ของวิดีโอที่อัปโหลดไปยัง Azure Blob Storage
    video_url = f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net/{settings.AZURE_CONTAINER_NAME}/{blob_name}"
    return JSONResponse({"video_url": video_url})
'''

'''
@vehicle_router.post("/predictimg2/")
async def predict(file: UploadFile = File(...)):
    # Check the file extension to ensure it is an image
    if not file.filename.endswith(('.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PNG and JPEG images are accepted.")
    
    # Read the file contents
    contents = await file.read()
    
    try:
        # Open the image using PIL
        image = Image.open(io.BytesIO(contents))
        
        # Convert image to numpy array
        img_np = np.array(image)
        
        # Make predictions using YOLO
        results = model(img_np)
        
        # Draw the results on the image
        result_image = results[0].plot()
        
        # Convert back to PIL Image
        result_pil_image = Image.fromarray(result_image)

        # Create a byte stream to send back to the client
        byte_io = io.BytesIO()
        result_pil_image.save(byte_io, format='PNG')
        byte_io.seek(0)

        # Send image back as response
        return StreamingResponse(byte_io, media_type="image/png")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing the image: {str(e)}")
'''