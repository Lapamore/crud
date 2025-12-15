from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core import get_db, get_current_user, AuthenticatedUser
from ..models.commands import (
    CreateArticleCommand, 
    UpdateArticleCommand,
    DeleteArticleCommand
)

from ..models.queries import (
    GetArticleBySlugQuery,
    ListArticlesQuery
)

from ..handlers import (
    CreateArticleHandler,
    UpdateArticleHandler,
    DeleteArticleHandler,
    GetArticleBySlugHandler,
    ListArticlesHandler,
)
from ..repositories.impl import SqlAlchemyArticleWriteRepository, ArticleReadRepository
from ..exceptions import (
    SlugAlreadyExistsException,
    ArticleNotFoundException,
    NotAuthorizedToModifyArticleException,
)

router = APIRouter()


@router.post("/articles", response_model=schemas.ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(
    article: schemas.ArticleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    repository = SqlAlchemyArticleWriteRepository(db)
    handler = CreateArticleHandler(repository)
    
    command = CreateArticleCommand(
        title=article.title,
        description=article.description,
        body=article.body,
        author_id=current_user.id,
        tag_list=article.tagList,
    )
    
    try:
        article_id = await handler.handle(command)
    except SlugAlreadyExistsException:
        raise HTTPException(status_code=409, detail="Slug already exists")
    
    read_repository = ArticleReadRepository(db)
    query_handler = GetArticleBySlugHandler(read_repository)
    
    result = await read_repository.find_by_slug(command.title.lower().replace(" ", "-"))
    return result


@router.get("/articles", response_model=List[schemas.ArticleResponse])
async def list_articles(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    repository = ArticleReadRepository(db)
    handler = ListArticlesHandler(repository)
    
    query = ListArticlesQuery(skip=skip, limit=limit)
    articles = await handler.handle(query)
    
    return [
        {
            "id": a.id,
            "slug": a.slug,
            "title": a.title,
            "description": a.description,
            "body": a.body,
            "author_id": a.author_id,
            "tagList": a.tag_list,
        }
        for a in articles
    ]


@router.get("/articles/{slug}", response_model=schemas.ArticleResponse)
async def get_article(slug: str, db: AsyncSession = Depends(get_db)):
    repository = ArticleReadRepository(db)
    handler = GetArticleBySlugHandler(repository)
    
    query = GetArticleBySlugQuery(slug=slug)
    
    try:
        article = await handler.handle(query)
    except ArticleNotFoundException:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return {
        "id": article.id,
        "slug": article.slug,
        "title": article.title,
        "description": article.description,
        "body": article.body,
        "author_id": article.author_id,
        "tagList": article.tag_list,
    }


@router.put("/articles/{slug}", response_model=schemas.ArticleResponse)
async def update_article(
    slug: str,
    article_in: schemas.ArticleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    repository = SqlAlchemyArticleWriteRepository(db)
    handler = UpdateArticleHandler(repository)
    
    command = UpdateArticleCommand(
        slug=slug,
        user_id=current_user.id,
        title=article_in.title,
        description=article_in.description,
        body=article_in.body,
        tag_list=article_in.tagList,
    )
    
    try:
        await handler.handle(command)
    except ArticleNotFoundException:
        raise HTTPException(status_code=404, detail="Article not found")
    except NotAuthorizedToModifyArticleException:
        raise HTTPException(status_code=403, detail="Not authorized to update this article")
    
    read_repository = ArticleReadRepository(db)
    updated_article = await read_repository.find_by_slug(
        command.title.lower().replace(" ", "-") if command.title else slug
    )
    return updated_article


@router.delete("/articles/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    repository = SqlAlchemyArticleWriteRepository(db)
    handler = DeleteArticleHandler(repository)
    
    command = DeleteArticleCommand(slug=slug, user_id=current_user.id)
    
    try:
        await handler.handle(command)
    except ArticleNotFoundException:
        raise HTTPException(status_code=404, detail="Article not found")
    except NotAuthorizedToModifyArticleException:
        raise HTTPException(status_code=403, detail="Not authorized to delete this article")
    
    return
