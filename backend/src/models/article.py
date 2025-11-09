import sqlalchemy as sa
from ..database import Base


class Article(Base):
    __tablename__ = "articles"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    slug = sa.Column(sa.String, unique=True, index=True, nullable=False)
    title = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String, nullable=False)
    body = sa.Column(sa.String, nullable=False)
    author_id = sa.Column(sa.Integer, nullable=False)
    tagList = sa.Column(sa.ARRAY(sa.String), nullable=True)