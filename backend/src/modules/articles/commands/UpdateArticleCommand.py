from dataclasses import dataclass
from typing import Optional, List


@dataclass(frozen=True)
class UpdateArticleCommand:
    slug: str
    user_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    body: Optional[str] = None
    tag_list: Optional[List[str]] = None
