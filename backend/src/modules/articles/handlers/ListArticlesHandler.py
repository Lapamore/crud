from typing import List
from ..queries.ListArticlesQuery import ListArticlesQuery
from ..repositories.core.IArticleReadRepository import IArticleReadRepository
from ..dto.ArticleDTO import ArticleDTO


class ListArticlesHandler:
    def __init__(self, repository: IArticleReadRepository):
        self._repository = repository

    async def handle(self, query: ListArticlesQuery) -> List[ArticleDTO]:
        articles = await self._repository.find_all(query.skip, query.limit)
        
        return [
            ArticleDTO(
                id=article.id,
                slug=article.slug,
                title=article.title,
                description=article.description,
                body=article.body,
                author_id=article.author_id,
                tag_list=article.tags,
            )
            for article in articles
        ]
