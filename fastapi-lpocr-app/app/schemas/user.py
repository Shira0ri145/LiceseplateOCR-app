from datetime import datetime
from pydantic import BaseModel, EmailStr

class RegisterUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginUserRequest(BaseModel):
    email: EmailStr
    password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    new_password: str
    confirm_new_password: str 

class LoginUserResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class UsersResponse(BaseModel):
    username: str
    email: EmailStr
    is_verified: bool
    verified_at: datetime
