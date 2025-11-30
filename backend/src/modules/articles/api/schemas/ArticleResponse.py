from .ArticleBase import ArticleBase


class ArticleResponse(ArticleBase):
    id: int
    slug: str
    author_id: int

    class Config:
        from_attributes = True
