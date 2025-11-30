from dataclasses import dataclass


@dataclass(frozen=True)
class DeleteCommentCommand:
    comment_id: int
    user_id: int
