from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.config.database import db_dependency
from app.config.dependencies import AccessTokenBearer, RoleChecker

# Create a new APIRouter instance for vehicle-related routes
vehicle_router = APIRouter(
    prefix='/vehicle',
    tags=['Vehicle']
)
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(["admin","member"]))

@vehicle_router.get('/',dependencies=[role_checker])
async def hello(
    vehicle_details=Depends(access_token_bearer)):
    return {"message": "welcome to vehicle page"}

# Temporary storage for uploaded files
uploaded_files = []

@vehicle_router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_vehicle_file(file: UploadFile = File(...)):
    # Check if the uploaded file is a video or image
    if not file.content_type.startswith(('image/', 'video/')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only images and videos are allowed."
        )

    # Simulate saving the file information to memory (in this case, list)
    uploaded_files.append(file.filename)
    
    return JSONResponse(content={"message": "File uploaded successfully", "filename": file.filename})

@vehicle_router.get("/uploads", status_code=status.HTTP_200_OK)
async def get_uploaded_files():
    # Return the list of uploaded files
    return JSONResponse(content={"uploaded_files": uploaded_files})