from ....dto import ArticleDTO
from ....exceptions import ArticleNotFoundException
from ....repositories.core import IArticleReadRepository

__all__ = ["GetArticleBySlugHandler"]


class GetArticleBySlugHandler:
    def __init__(self, repository: IArticleReadRepository):
        self._repository = repository

    async def handle(self, query: GetArticleBySlugQuery) -> ArticleDTO:
        article = await self._repository.find_by_slug(query.slug)
        
        if article is None:
            raise ArticleNotFoundException(query.slug)

        return ArticleDTO(
            id=article.id,
            slug=article.slug,
            title=article.title,
            description=article.description,
            body=article.body,
            author_id=article.author_id,
            tag_list=article.tags,
        )
