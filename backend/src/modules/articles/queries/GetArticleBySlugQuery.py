from dataclasses import dataclass


@dataclass(frozen=True)
class GetArticleBySlugQuery:
    slug: str
