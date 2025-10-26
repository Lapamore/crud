import sqlalchemy as sa
from sqlalchemy.orm import relationship

from ..database import Base


class Article(Base):
    __tablename__ = "articles"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    slug = sa.Column(sa.String, unique=True, index=True, nullable=False)
    title = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String, nullable=False)
    body = sa.Column(sa.String, nullable=False)
    author_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))

    author = relationship("User", back_populates="articles")
    comments = relationship("Comment", back_populates="article")
    # tagList will be handled as a separate table or a string
    tags = sa.Column("tagList", sa.ARRAY(sa.String), nullable=True)
