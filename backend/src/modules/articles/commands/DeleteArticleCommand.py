from dataclasses import dataclass


@dataclass(frozen=True)
class DeleteArticleCommand:
    slug: str
    user_id: int
