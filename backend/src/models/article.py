import sqlalchemy as sa
from sqlalchemy.orm import relationship
from database import Base
from core.enums import ArticleStatus


class Article(Base):
    __tablename__ = "articles"
    __table_args__ = {'extend_existing': True}

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    slug = sa.Column(sa.String, unique=True, index=True, nullable=False)
    title = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String, nullable=False)
    body = sa.Column(sa.String, nullable=False)
    author_id = sa.Column(sa.Integer, nullable=False)
    comments = relationship("Comment", back_populates="article", cascade="all, delete-orphan")
    tags = sa.Column("tagList", sa.ARRAY(sa.String), nullable=True)
    
    status = sa.Column(sa.String(20), default=ArticleStatus.DRAFT.value, nullable=False)
    preview_url = sa.Column(sa.String, nullable=True)