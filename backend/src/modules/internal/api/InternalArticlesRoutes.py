from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.deps import get_db, verify_internal_api_key
from core.enums import ArticleStatus
from models import Article
from .schemas import (
    ArticleInternalResponse,
    UpdatePreviewRequest,
    RejectRequest,
    SetErrorRequest
)

router = APIRouter()


@router.get("/posts/{post_id}", response_model=ArticleInternalResponse)
async def get_post_internal(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_internal_api_key)
):
    """
    Получение поста по ID (внутренний эндпоинт).
    Доступен только с валидным внутренним API-ключом.
    """
    query = select(Article).where(Article.id == post_id)
    result = await db.execute(query)
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return ArticleInternalResponse(
        id=article.id,
        slug=article.slug,
        title=article.title,
        description=article.description,
        body=article.body,
        author_id=article.author_id,
        status=article.status,
        preview_url=article.preview_url,
        tagList=article.tags
    )


@router.post("/posts/{post_id}/reject")
async def reject_post(
    post_id: int,
    reject_data: RejectRequest = None,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_internal_api_key)
):
    """
    Отклонение поста модерацией (внутренний эндпоинт).
    Переводит статус из PENDING_PUBLISH в REJECTED.
    Идемпотентная операция.
    """
    query = select(Article).where(Article.id == post_id)
    result = await db.execute(query)
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Идемпотентность: если уже REJECTED, просто возвращаем успех
    if article.status == ArticleStatus.REJECTED.value:
        return {"message": "Article already rejected", "status": article.status}
    
    # Проверяем, что пост в состоянии PENDING_PUBLISH
    if article.status not in [ArticleStatus.PENDING_PUBLISH.value, ArticleStatus.ERROR.value]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot reject article with status {article.status}"
        )
    
    article.status = ArticleStatus.REJECTED.value
    await db.commit()
    
    return {"message": "Article rejected", "status": article.status}


@router.put("/posts/{post_id}/preview")
async def update_preview(
    post_id: int,
    preview_data: UpdatePreviewRequest,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_internal_api_key)
):
    """
    Обновление preview_url поста (внутренний эндпоинт).
    Вызывается Preview Worker после генерации превью.
    """
    query = select(Article).where(Article.id == post_id)
    result = await db.execute(query)
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    article.preview_url = preview_data.preview_url
    await db.commit()
    
    return {"message": "Preview updated", "preview_url": article.preview_url}


@router.post("/posts/{post_id}/publish")
async def publish_post_internal(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_internal_api_key)
):
    """
    Публикация поста (внутренний эндпоинт).
    Переводит статус из PENDING_PUBLISH в PUBLISHED.
    Идемпотентная операция.
    """
    query = select(Article).where(Article.id == post_id)
    result = await db.execute(query)
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Идемпотентность: если уже PUBLISHED, просто возвращаем успех
    if article.status == ArticleStatus.PUBLISHED.value:
        return {"message": "Article already published", "status": article.status}
    
    # Проверяем, что пост в состоянии PENDING_PUBLISH
    if article.status != ArticleStatus.PENDING_PUBLISH.value:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot publish article with status {article.status}"
        )
    
    article.status = ArticleStatus.PUBLISHED.value
    await db.commit()
    
    return {
        "message": "Article published",
        "status": article.status,
        "author_id": article.author_id,
        "title": article.title
    }


@router.post("/posts/{post_id}/error")
async def set_post_error(
    post_id: int,
    error_data: SetErrorRequest = None,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_internal_api_key)
):
    """
    Установка статуса ERROR для поста (внутренний эндпоинт).
    Используется для компенсации при технических ошибках.
    Идемпотентная операция.
    """
    query = select(Article).where(Article.id == post_id)
    result = await db.execute(query)
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Идемпотентность: если уже ERROR, просто возвращаем успех
    if article.status == ArticleStatus.ERROR.value:
        return {"message": "Article already in error state", "status": article.status}
    
    # Можем установить ERROR из любого состояния кроме PUBLISHED
    if article.status == ArticleStatus.PUBLISHED.value:
        raise HTTPException(
            status_code=400,
            detail="Cannot set error status for published article"
        )
    
    article.status = ArticleStatus.ERROR.value
    await db.commit()
    
    return {"message": "Article set to error state", "status": article.status}


@router.post("/posts/{post_id}/reset-to-draft")
async def reset_to_draft(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_internal_api_key)
):
    """
    Сброс статуса поста в DRAFT (внутренний эндпоинт).
    Используется для компенсации при ошибках.
    """
    query = select(Article).where(Article.id == post_id)
    result = await db.execute(query)
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Нельзя сбросить уже опубликованный пост
    if article.status == ArticleStatus.PUBLISHED.value:
        raise HTTPException(
            status_code=400,
            detail="Cannot reset published article to draft"
        )
    
    article.status = ArticleStatus.DRAFT.value
    await db.commit()
    
    return {"message": "Article reset to draft", "status": article.status}
