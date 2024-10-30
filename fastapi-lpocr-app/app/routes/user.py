from fastapi import APIRouter, Depends, status , HTTPException
from fastapi.responses import JSONResponse

from app.config.database import db_dependency
from app.services.user import (
    create_user, 
    get_new_access_token_from_service, 
    login_user,
    reset_password_request,
    reset_password_with_token, 
    verify_email)
from app.schemas.user import (
    LoginUserRequest,
    PasswordResetConfirm,
    PasswordResetRequest, 
    RegisterUserRequest)
from app.config.dependencies import (
    RefreshTokenBearer,
    AccessTokenBearer,
    get_current_user,
    RoleChecker)
from app.config.redis import add_jti_to_blocklist

# Create a new APIRouter instance for authentication
auth_router = APIRouter(
    prefix='/auth',
    tags=['auth'],
    responses={404: {"description": "Not found"}},
)
role_checker = RoleChecker(["admin","member"])

@auth_router.get('/')
async def hello():
    return {"message": "hello"}

@auth_router.post('/signup')
async def signup(user: RegisterUserRequest, db: db_dependency):
    db_user = await create_user(db, user) 
    # return db_user
    if db_user:
        return {"message": "User created successfully", "user": user.username}
    
@auth_router.get('/verification')
async def email_verification(db: db_dependency, token : str):
    user = await verify_email(token, db)
    
    return {
        "message": "Email Verified Successfully",
        "username": user.username,
        "detail": "You can now log in to your account."
    }

@auth_router.post('/login')
async def login_users(login: LoginUserRequest, db: db_dependency):
    response = await login_user(db, login.email, login.password)
    return JSONResponse(content=response)

@auth_router.get('/refresh_token')
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    return await get_new_access_token_from_service(token_details)

@auth_router.get('/profile')
async def get_current_user(user_and_role: tuple = Depends(get_current_user), _: bool = Depends(role_checker)   ):
    user, role = user_and_role
    return {
        "username": user.username,
        "email": user.email,
        "is_verified": user.is_verified,
        "created_at": user.created_at,
        "role": role
    }

@auth_router.get('/logout')
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details['jti']

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={
            "message":"Logged Out Successfully"
        },
        status_code=status.HTTP_200_OK
    )

@auth_router.post('/reset-password')
async def password_reset_request(email_data: PasswordResetRequest, db: db_dependency):
    password_request = await reset_password_request(db, email_data.email)
    return password_request

@auth_router.post("/password-reset-confirm/{token}")
async def reset_account_password(
    token: str,
    passwords: PasswordResetConfirm,
    db: db_dependency,
):
    return await reset_password_with_token(db, token, passwords.new_password, passwords.confirm_new_password)