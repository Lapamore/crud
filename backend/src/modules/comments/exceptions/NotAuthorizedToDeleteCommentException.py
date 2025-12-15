__all__ = ["NotAuthorizedToDeleteCommentException"]


class NotAuthorizedToDeleteCommentException(Exception):
    def __init__(self):
        super().__init__("Not authorized to delete this comment")
