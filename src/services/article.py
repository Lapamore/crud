from slugify import slugify
from sqlalchemy.orm import Session
from .. import models, schemas


def create_article(db: Session, article: schemas.ArticleCreate, author_id: int):
    slug = slugify(article.title)
    db_article = models.Article(
        title=article.title,
        description=article.description,
        body=article.body,
        slug=slug,
        author_id=author_id,
    )

    
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article


def get_articles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Article).offset(skip).limit(limit).all()

def get_article_by_title(db: Session, title: str):
    return db.query(models.Article).filter(models.Article.title == title)

def get_article_by_slug(db: Session, slug: str):
    return db.query(models.Article).filter(models.Article.slug == slug).first()

def update_article(db: Session, db_article: models.Article, article_in: schemas.ArticleUpdate):
    update_data = article_in.model_dump(exclude_unset=True)
    if "title" in update_data:
        db_article.slug = slugify(update_data["title"])

    for field, value in update_data.items():
        setattr(db_article, field, value)

    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article


def delete_article(db: Session, db_article: models.Article):
    db.delete(db_article)
    db.commit()
