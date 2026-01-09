from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import ApiKey
from ..core.IApiKeyRepository import IApiKeyRepository


class SqlAlchemyApiKeyRepository(IApiKeyRepository):
    
    def __init__(self, db: AsyncSession):
        self._db = db

    async def find_by_key(self, key: str) -> Optional[ApiKey]:
        query = select(ApiKey).where(
            ApiKey.key == key,
            ApiKey.is_active == True
        )
        result = await self._db.execute(query)
        api_key = result.scalar_one_or_none()
        
        if api_key and api_key.expires_at and api_key.expires_at < datetime.utcnow():
            return None
            
        return api_key

    async def create(self, key: str, description: str, expires_at: Optional[datetime] = None) -> ApiKey:
        api_key = ApiKey(
            key=key,
            description=description,
            expires_at=expires_at,
            is_active=True
        )
        self._db.add(api_key)
        await self._db.commit()
        await self._db.refresh(api_key)
        return api_key

    async def deactivate(self, key_id: int) -> None:
        query = select(ApiKey).where(ApiKey.id == key_id)
        result = await self._db.execute(query)
        api_key = result.scalar_one_or_none()
        if api_key:
            api_key.is_active = False
            await self._db.commit()
