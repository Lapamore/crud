from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .. import schemas
from ..services import article as article_service
from .deps import get_db, get_current_user
from ..schemas import AuthenticatedUser

router = APIRouter()


@router.post("/articles", response_model=schemas.Article, status_code=status.HTTP_201_CREATED)
async def create_article(
    article: schemas.ArticleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    return await article_service.create_article(db=db, article=article, author_id=current_user.id)
    
@router.get("/articles", response_model=List[schemas.Article])
async def list_articles(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    return await article_service.get_articles(db, skip=skip, limit=limit)

@router.get("/articles/{slug}", response_model=schemas.Article)
async def get_article(slug: str, db: AsyncSession = Depends(get_db)):
    db_article = await article_service.get_article_by_slug(db, slug=slug)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return db_article


@router.put("/articles/{slug}", response_model=schemas.Article)
async def update_article(
    slug: str,
    article_in: schemas.ArticleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user) # <-- Тип верный
):
    db_article = await article_service.get_article_by_slug(db, slug=slug)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    if db_article.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this article")
    return await article_service.update_article(db=db, db_article=db_article, article_in=article_in)


@router.delete("/articles/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user) # <-- ИСПРАВЛЕНО ЗДЕСЬ
):
    db_article = await article_service.get_article_by_slug(db, slug=slug)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    if db_article.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this article")
    await article_service.delete_article(db=db, db_article=db_article)
    return