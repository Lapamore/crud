from typing import AsyncGenerator, Optional
from datetime import datetime

from celery import Celery
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from fastapi import Depends, HTTPException, status, Header

from config import settings
from database import AsyncSessionLocal
from models import ApiKey

from core.tasker.impl.CeleryTaskProducer import CeleryTaskProducer
from core.tasker.core.ITaskProducer import ITaskProducer
from core.schemas.AuthenticatedUser import AuthenticatedUser


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(token: str = Depends(oauth2_scheme)) -> AuthenticatedUser:
    """Аутентификация пользователя по JWT токену."""
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


async def verify_internal_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db)
) -> bool:
    """
    Проверка внутреннего API-ключа для service-to-service коммуникаций.
    Используется для внутренних эндпоинтов, недоступных обычным пользователям.
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Internal API key required",
        )
    
    query = select(ApiKey).where(
        ApiKey.key == x_api_key,
        ApiKey.is_active == True
    )
    result = await db.execute(query)
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    
    if api_key.expires_at and api_key.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key has expired",
        )
    
    return True


def get_task_producer() -> ITaskProducer:
    celery_app = Celery(
        "backend",
        broker=settings.REDIS_URL
    )

    return CeleryTaskProducer(celery_app)