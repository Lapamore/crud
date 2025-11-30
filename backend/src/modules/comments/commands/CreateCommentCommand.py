from dataclasses import dataclass


@dataclass(frozen=True)
class CreateCommentCommand:
    body: str
    article_id: int
    author_id: int
