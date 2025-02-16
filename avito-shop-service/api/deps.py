from typing import Annotated, AsyncGenerator
from jose import JWTError, jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.engine import async_session

from repository.unit_of_work import UnitOfWork
from models import User
from services.user import UserService
from exceptions.app_exception import InvalidCredentialsError, UserNotFoundError

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
        
def get_uow(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UnitOfWork:
    return UnitOfWork(db)


def get_user_service(
    uow: Annotated[UnitOfWork, Depends(get_uow)]
) -> UserService:
    return UserService(uow)


reusable_oauth2 = HTTPBearer()

async def get_current_user(
    uow: Annotated[UnitOfWork, Depends(get_uow)],
    credentials: HTTPAuthorizationCredentials = Depends(reusable_oauth2),
) -> User:
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        if (username := payload.get("sub")) is None:
            raise InvalidCredentialsError()
            
    except JWTError as exc:
        raise InvalidCredentialsError() from exc

    try:
        user = await uow.users.get_by_username(username=username)
    except Exception as exc:
        raise UserNotFoundError() from exc
        
    if not user:
        raise UserNotFoundError()
        
    return user

