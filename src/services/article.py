from slugify import slugify
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .. import models, schemas


async def create_article(db: AsyncSession, article: schemas.ArticleCreate, author_id: int):
    slug = slugify(article.title)
    if await get_article_by_slug(db, slug=slug):
        raise HTTPException(status_code=409, detail="Slug already exists")

    db_article = models.Article(
        title=article.title,
        description=article.description,
        body=article.body,
        slug=slug,
        author_id=author_id,
        tags=article.tagList,
    )
    db.add(db_article)
    await db.commit()
    await db.refresh(db_article)
    return db_article


async def get_articles(db: AsyncSession, skip: int = 0, limit: int = 100):
    query = select(models.Article).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def get_article_by_slug(db: AsyncSession, slug: str):
    query = select(models.Article).where(models.Article.slug == slug)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def update_article(db: AsyncSession, db_article: models.Article, article_in: schemas.ArticleUpdate):
    update_data = article_in.model_dump(exclude_unset=True)
    if "title" in update_data:
        db_article.slug = slugify(update_data["title"])

    for field, value in update_data.items():
        setattr(db_article, field, value)

    db.add(db_article)
    await db.commit()
    await db.refresh(db_article)
    return db_article


async def delete_article(db: AsyncSession, db_article: models.Article):
    await db.delete(db_article)
    await db.commit()