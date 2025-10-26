from sqlalchemy.orm import Session
from .. import models, schemas


def create_comment(db: Session, comment: schemas.CommentCreate, article_id: int, author_id: int):
    db_comment = models.Comment(
        **comment.model_dump(),
        article_id=article_id,
        author_id=author_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_comments_by_article_slug(db: Session, slug: str):
    return db.query(models.Comment).join(models.Article).filter(models.Article.slug == slug).all()


def get_comment(db: Session, comment_id: int):
    return db.query(models.Comment).filter(models.Comment.id == comment_id).first()


def delete_comment(db: Session, db_comment: models.Comment):
    db.delete(db_comment)
    db.commit()
