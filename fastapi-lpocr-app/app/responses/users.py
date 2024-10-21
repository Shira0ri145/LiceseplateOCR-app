from typing import Union
from datetime import datetime
from pydantic import EmailStr, BaseModel
from app.responses.base import BaseResponse


class UserResponse(BaseResponse):
    user_id: int
    username: str
    email: EmailStr
    is_verified: bool
    image_url: str
    created_at: Union[str, None, datetime] = None
    