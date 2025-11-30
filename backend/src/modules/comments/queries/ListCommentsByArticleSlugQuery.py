from dataclasses import dataclass


@dataclass(frozen=True)
class ListCommentsByArticleSlugQuery:
    slug: str
