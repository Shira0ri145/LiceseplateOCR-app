from pydantic import BaseModel, HttpUrl
from datetime import datetime

class UploadFileCreate(BaseModel):
    upload_name: str
    upload_type: str
    upload_url: str
    obj_detect_url: str

class UploadFileResponse(BaseModel):
    id: int
    user_id: int
    upload_name: str
    upload_url: HttpUrl
    obj_detect_url: HttpUrl
    upload_type: str
    created_at: datetime

class UploadFileSchema(BaseModel):
    id: int
    user_id: int
    upload_name: str
    upload_url: HttpUrl
    upload_type: str
    created_at: datetime