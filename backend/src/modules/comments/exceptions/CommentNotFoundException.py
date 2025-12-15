__all__ = ["CommentNotFoundException"]


class CommentNotFoundException(Exception):
    def __init__(self, comment_id: int):
        self.comment_id = comment_id
        super().__init__(f"Comment with id '{comment_id}' not found")
