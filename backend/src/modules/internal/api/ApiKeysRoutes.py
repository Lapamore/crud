import secrets
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.deps import get_db
from models import ApiKey
from .schemas import ApiKeyCreate, ApiKeyResponse, InitKeysResponse

router = APIRouter()


@router.post("/init-keys", response_model=InitKeysResponse)
async def initialize_internal_api_keys(
    db: AsyncSession = Depends(get_db)
):
    query = select(ApiKey).where(ApiKey.is_active == True)
    result = await db.execute(query)
    existing_keys = result.scalars().all()
    
    if existing_keys:
        return InitKeysResponse(
            message="API keys already exist",
            keys=[
                ApiKeyResponse(
                    id=k.id,
                    key=k.key,
                    description=k.description,
                    is_active=k.is_active
                )
                for k in existing_keys
            ]
        )
    
    worker_names = [
        "moderation-worker",
        "preview-worker",
        "publish-worker",
        "notification-worker",
        "dlq-worker"
    ]
    
    created_keys = []
    for worker_name in worker_names:
        key = secrets.token_urlsafe(48)
        api_key = ApiKey(
            key=key,
            description=f"Internal API key for {worker_name}",
            is_active=True
        )
        db.add(api_key)
        created_keys.append(api_key)
    
    await db.commit()
    
    for k in created_keys:
        await db.refresh(k)
    
    return InitKeysResponse(
        message="API keys created successfully",
        keys=[
            ApiKeyResponse(
                id=k.id,
                key=k.key,
                description=k.description,
                is_active=k.is_active
            )
            for k in created_keys
        ]
    )


@router.post("/create-key", response_model=ApiKeyResponse)
async def create_api_key(
    key_data: ApiKeyCreate,
    db: AsyncSession = Depends(get_db)
):
    key = secrets.token_urlsafe(48)
    api_key = ApiKey(
        key=key,
        description=key_data.description,
        is_active=True
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)
    
    return ApiKeyResponse(
        id=api_key.id,
        key=api_key.key,
        description=api_key.description,
        is_active=api_key.is_active
    )
