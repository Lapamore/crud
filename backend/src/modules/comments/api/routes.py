from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from . import schemas
from src.core import get_db, get_current_user, AuthenticatedUser
from ..commands import CreateCommentCommand, DeleteCommentCommand
from ..queries import ListCommentsByArticleSlugQuery
from ..handlers import (
    CreateCommentHandler,
    DeleteCommentHandler,
    ListCommentsByArticleSlugHandler,
)
from ..repositories.impl import SqlAlchemyCommentWriteRepository, SqlAlchemyCommentReadRepository
from ..exceptions import CommentNotFoundException, NotAuthorizedToDeleteCommentException
from ...articles.repositories.impl import SqlAlchemyArticleReadRepository

router = APIRouter()


@router.post("/articles/{slug}/comments", response_model=schemas.CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment_for_article(
    slug: str,
    comment: schemas.CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    article_repo = SqlAlchemyArticleReadRepository(db)
    article = await article_repo.find_by_slug(slug)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    
    repository = SqlAlchemyCommentWriteRepository(db)
    handler = CreateCommentHandler(repository)
    
    command = CreateCommentCommand(
        body=comment.body,
        article_id=article.id,
        author_id=current_user.id,
    )
    
    comment_id = await handler.handle(command)
    
    read_repo = SqlAlchemyCommentReadRepository(db)
    saved_comment = await read_repo.find_by_id(comment_id)
    return saved_comment


@router.get("/articles/{slug}/comments", response_model=List[schemas.CommentResponse])
async def get_comments_for_article(slug: str, db: AsyncSession = Depends(get_db)):
    article_repo = SqlAlchemyArticleReadRepository(db)
    article = await article_repo.find_by_slug(slug)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    
    repository = SqlAlchemyCommentReadRepository(db)
    handler = ListCommentsByArticleSlugHandler(repository)
    
    query = ListCommentsByArticleSlugQuery(slug=slug)
    comments = await handler.handle(query)
    
    return [
        {"id": c.id, "body": c.body, "article_id": c.article_id, "author_id": c.author_id}
        for c in comments
    ]


@router.delete("/articles/{slug}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    slug: str,
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    article_repo = SqlAlchemyArticleReadRepository(db)
    article = await article_repo.find_by_slug(slug)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    
    repository = SqlAlchemyCommentWriteRepository(db)
    handler = DeleteCommentHandler(repository)
    
    command = DeleteCommentCommand(comment_id=comment_id, user_id=current_user.id)
    
    try:
        await handler.handle(command)
    except CommentNotFoundException:
        raise HTTPException(status_code=404, detail="Comment not found")
    except NotAuthorizedToDeleteCommentException:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    
    return
