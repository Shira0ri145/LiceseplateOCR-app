from typing import Any, List
from fastapi import Request, status, Depends
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from app.config.security import decode_token
from app.config.redis import token_in_blocklist
from fastapi.exceptions import HTTPException
from app.config.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Users
from app.services.user import get_rolename_by_usersroles, get_user_by_email


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        token = creds.credentials

        token_data = decode_token(token)

        if not self.token_valid(token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error":"This token is invalid or expired",
                    "resolution":"Please get new token"
                }
            )
        
        if await token_in_blocklist(token_data["jti"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error":"This token is invalid or has been revoked",
                    "resolution":"Please get new token"
                }
            )


        self.verify_token_data(token_data)

        return token_data
    
    def token_valid(self,token: str) -> bool:
        token_data = decode_token( token)

        return token_data is not None
    
    def verify_token_data(self, token_data):
        raise NotImplementedError("Please Override this method in child classes")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide an access token"
            )


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide a refresh token"
            )
        
async def get_current_user(token_details: dict = Depends(AccessTokenBearer()),
                           db: AsyncSession = Depends(get_db)):
    user_email = token_details['user']['email']
    user = await get_user_by_email(db, user_email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    role = await get_rolename_by_usersroles(db, user.id)
    
    return user,role

class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:

        self.allowed_roles = allowed_roles

    def __call__(self, current_user_role: tuple = Depends(get_current_user)) -> Any:
        current_user, role = current_user_role
        if not current_user.is_verified:
            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account not verified"
        )

        if role in self.allowed_roles:  # ตรวจสอบบทบาท
            return True
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to perform this action"
        )
