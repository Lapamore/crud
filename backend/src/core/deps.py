from typing import AsyncGenerator

from celery import Celery
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

from config import settings
from database import AsyncSessionLocal

from core.tasker.impl.CeleryTaskProducer import CeleryTaskProducer
from core.tasker.core.ITaskProducer import ITaskProducer
from core.schemas.AuthenticatedUser import AuthenticatedUser


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

async def get_current_user(token: str = Depends(oauth2_scheme)) -> AuthenticatedUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id: int = payload.get("id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return AuthenticatedUser(id=user_id, username=payload.get("sub"))

def get_task_producer() -> ITaskProducer:
    celery_app = Celery(
        "backend",
        broker=settings.REDIS_URL
    )

    return CeleryTaskProducer(celery_app)