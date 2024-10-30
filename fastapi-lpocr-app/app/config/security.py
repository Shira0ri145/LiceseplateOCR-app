from datetime import datetime, timedelta
from fastapi.exceptions import HTTPException
from fastapi import status
from passlib.context import CryptContext
import jwt
import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.config.settings import get_settings
from app.models.user import Users


SPECIAL_CHARACTERS = ['@', '#', '$', '%', '=', ':', '?', '.', '/', '|', '~', '>']

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def is_password_strong_enough(password: str) -> bool:
    if len(password) < 8:
        return False

    if not any(char.isupper() for char in password):
        return False

    if not any(char.islower() for char in password):
        return False

    if not any(char.isdigit() for char in password):
        return False

    if not any(char in SPECIAL_CHARACTERS for char in password):
        return False

    return True

async def get_token_payload(token: str, db: AsyncSession):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get("id")
        
        # ตรวจสอบว่ามีผู้ใช้หรือไม่
        result = await db.execute(select(Users).where(Users.id == user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"}
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.PyJWTError:  # ใช้ PyJWTError แทน JWTError
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user

ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict, expiry: timedelta = None, refresh: bool= False):
    payload = {}

    payload["user"] = data
    payload["exp"] = datetime.now() + (
        expiry if expiry is not None else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload['jti'] = str(uuid.uuid4())
    payload['refresh'] = refresh

    token = jwt.encode(
        payload=payload, key=settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    
    return token

def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(jwt=token, key=settings.SECRET_KEY, algorithms=settings.JWT_ALGORITHM)

        return token_data
    except jwt.PyJWTError as e:
        logging.exception(e)
        return None


from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
