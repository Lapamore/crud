from .CommentBase import CommentBase


class CommentResponse(CommentBase):
    id: int
    article_id: int
    author_id: int

    class Config:
        from_attributes = True
