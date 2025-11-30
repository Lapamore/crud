from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CommentDTO:
    id: int
    body: str
    article_id: int
    author_id: int
