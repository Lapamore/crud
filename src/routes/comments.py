from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..services import article as article_service
from ..services import comment as comment_service
from .deps import get_db, get_current_user

router = APIRouter()


@router.post("/articles/{slug}/comments", response_model=schemas.Comment, status_code=status.HTTP_201_CREATED)
def create_comment_for_article(
    slug: str,
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_article = article_service.get_article_by_slug(db, slug=slug)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return comment_service.create_comment(
        db=db, comment=comment, article_id=db_article.id, author_id=current_user.id
    )


@router.get("/articles/{slug}/comments", response_model=List[schemas.Comment])
def get_comments_for_article(slug: str, db: Session = Depends(get_db)):
    db_article = article_service.get_article_by_slug(db, slug=slug)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return comment_service.get_comments_by_article_slug(db=db, slug=slug)


@router.delete("/articles/{slug}/comments/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    slug: str,
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_article = article_service.get_article_by_slug(db, slug=slug)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    db_comment = comment_service.get_comment(db, comment_id=id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    if db_comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    comment_service.delete_comment(db=db, db_comment=db_comment)
    return
