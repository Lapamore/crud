from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .. import models, schemas


async def create_comment(db: AsyncSession, comment: schemas.CommentCreate, article_id: int, author_id: int):
    db_comment = models.Comment(
        **comment.model_dump(),
        article_id=article_id,
        author_id=author_id
    )
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    return db_comment


async def get_comments_by_article_slug(db: AsyncSession, slug: str):
    query = select(models.Comment).join(models.Article).filter(models.Article.slug == slug)
    result = await db.execute(query)
    return result.scalars().all()


async def get_comment(db: AsyncSession, comment_id: int):
    result = await db.execute(select(models.Comment).filter(models.Comment.id == comment_id))
    return result.scalar_one_or_none()


async def delete_comment(db: AsyncSession, db_comment: models.Comment):
    await db.delete(db_comment)
    await db.commit()