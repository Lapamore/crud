from CommentBase import CommentBase

__all__ = ["CommentResponse"]


class CommentResponse(CommentBase):
    id: int
    article_id: int
    author_id: int

    class Config:
        from_attributes = True
