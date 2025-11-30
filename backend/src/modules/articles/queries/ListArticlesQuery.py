from dataclasses import dataclass


@dataclass(frozen=True)
class ListArticlesQuery:
    skip: int = 0
    limit: int = 100
