from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from app.config.security import (
    create_access_token,
    decode_token,
    hash_password,
    is_password_strong_enough,
    get_token_payload, 
    verify_password)

from app.models.user import (
    Users, 
    UsersRoles, 
    Roles)
from app.schemas.user import LoginUserRequest, LoginUserResponse, RegisterUserRequest
from sqlalchemy.future import select
from sqlalchemy import func, update
from app.services.email import send_account_verification_email, send_password_reset_email

REFRESH_TOKEN_EXPIRY = 2 
async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(Users).where(Users.email == email))
    return result.scalar_one_or_none()

async def get_rolename_by_usersroles(db: AsyncSession, user_id: int):
    # Query to get the role name for a given user_id
    role_query = (
        select(Roles.role_name)
        .join(UsersRoles, UsersRoles.role_id == Roles.id)
        .where(UsersRoles.user_id == user_id)
    )
    result = await db.execute(role_query)
    role = result.scalar_one_or_none()  # Get the single role name or None
    return role

async def create_user(db: AsyncSession, user: RegisterUserRequest):
    # Check if the user already exists
    result = await db.execute(select(Users).where(Users.email == user.email))
    user_exist = result.scalar_one_or_none()  # Use scalar_one_or_none to get the first result or None
    if user_exist:
        raise HTTPException(status_code=400, detail="Email already exists.")
    if not is_password_strong_enough(user.password):
        raise HTTPException(status_code=400, detail="Please provide a strong password.")

    hashed_password = hash_password(user.password)
    # Create a new user
    new_user = Users(
        username=user.username,
        email=user.email,
        password=hashed_password,
        is_verified=False,
        user_id=800000 + (await db.execute(select(func.count()).select_from(Users))).scalar_one(),  # user_id starts at 80000 and increments by 1
        modified_at=datetime.now()
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    member_role = await db.scalar(select(Roles).where(Roles.id == 0))

    # Ensure the role exists before assigning it
    if not member_role:
        raise HTTPException(status_code=500, detail="Default 'member' role not found.")

    # Assign the 'member' role to the user
    user_role = UsersRoles(user_id=new_user.id, role_id=member_role.id)
    db.add(user_role)
    await db.commit()

    await send_account_verification_email([new_user.email],new_user)
    return new_user

async def verify_email(token: str, db: AsyncSession):
    # รับข้อมูลผู้ใช้จาก token
    user = await get_token_payload(token, db)

    # ตรวจสอบว่าผู้ใช้ได้รับการยืนยันแล้วหรือไม่
    if user.is_verified:
        raise HTTPException(
            status_code=400,
            detail="User already verified"
        )

    # ทำเครื่องหมายว่าผู้ใช้ได้รับการยืนยันแล้ว
    user.is_verified = True
    user.verified_at = datetime.now()
    user.modified_at = datetime.now()
    
    db.add(user)

    stmt_roles = (
        update(UsersRoles)
        .where(UsersRoles.user_id == user.id)
        .values(modified_at=datetime.now())
    )
    
    await db.execute(stmt_roles)
    await db.commit()

    return user

async def login_user(db: AsyncSession, email: str, password: str):

    user = await get_user_by_email(db, email)

    if user is not None:
        password_valid = verify_password(password, user.password)

        if password_valid:

            role = await get_rolename_by_usersroles(db, user.id)

            access_token = create_access_token(
                data={
                    "email": user.email,
                    "user_uid": str(user.id),
                    "role": role,
                }
            )

            refresh_token = create_access_token(
                data={"email": user.email, "user_uid": str(user.id)},
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
            )

            return {
                "message": "Login successful",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {"email": user.email, "uid": str(user.user_id),"role":role},
            }

    raise HTTPException(status_code=403, detail="Invalid Email or Password")

async def get_new_access_token_from_service(token_details: dict):
    expiry_timestamp = token_details['exp']

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(data=token_details["user"])
        return JSONResponse(content={"access_token": new_access_token})

    raise HTTPException(status_code=400, detail="Invalid or expired token")

async def reset_password_request(db: AsyncSession, email: str):
    user = await get_user_by_email(db, email)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    await send_password_reset_email([email], user)

    return JSONResponse(
        content={
        "message": "Please check your email for instructions to reset your password",
    },
    status_code=200,
    )

async def reset_password_with_token(db: AsyncSession, token: str, new_password: str, confirm_password: str):
    # Decode the token and extract user ID
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user_id = payload.get("id")

    if new_password != confirm_password:
        raise HTTPException(detail="Passwords do not match", status_code=400)
    
    if not is_password_strong_enough(new_password):
        raise HTTPException(status_code=400, detail="Please provide a strong password.")

    # Update the user's password
    await update_user_password(db, user_id, new_password)

    return JSONResponse(
            content={"message": "Password reset Successfully"},
            status_code=200,
        )


async def update_user_password(db: AsyncSession, user_id: int, new_password: str):
    async with db.begin():
        result = await db.execute(select(Users).where(Users.id == user_id))
        user = result.scalar_one_or_none()
        
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        # Hash the new password
        user.password = hash_password(new_password) 
        db.add(user)
        await db.commit()