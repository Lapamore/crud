import sqlalchemy as sa
from sqlalchemy.orm import relationship

from database import Base

__all__ = ["Comment"]


class Comment(Base):
    __tablename__ = "comments"
    
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    body = sa.Column(sa.String, nullable=False)
    article_id = sa.Column(sa.Integer, sa.ForeignKey("articles.id"))
    author_id = sa.Column(sa.Integer, nullable=False)
    article = relationship("Article", back_populates="comments")