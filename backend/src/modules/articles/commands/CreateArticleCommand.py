from dataclasses import dataclass
from typing import Optional, List


@dataclass(frozen=True)
class CreateArticleCommand:
    title: str
    description: str
    body: str
    author_id: int
    tag_list: Optional[List[str]] = None
