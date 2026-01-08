from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from . import schemas
from core.tasker.core import ITaskProducer
from core.deps import get_db, get_current_user, get_task_producer
from core.schemas.AuthenticatedUser import AuthenticatedUser    
from ..commands import CreateArticleCommand, UpdateArticleCommand, DeleteArticleCommand, PublishArticleCommand
from ..queries import GetArticleBySlugQuery, ListArticlesQuery
from ..handlers import (
    CreateArticleHandler,
    UpdateArticleHandler,
    DeleteArticleHandler,
    GetArticleBySlugHandler,
    ListArticlesHandler,
    PublishArticleHandler,
    ArticleNotInDraftException,
)
from ..repositories.impl import SqlAlchemyArticleWriteRepository, SqlAlchemyArticleReadRepository
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
    current_user: AuthenticatedUser = Depends(get_current_user),
    task_producer: ITaskProducer = Depends(get_task_producer)
):
    repository = SqlAlchemyArticleWriteRepository(db)
    handler = CreateArticleHandler(repository, task_producer)
    
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
    
    read_repository = SqlAlchemyArticleReadRepository(db)
    query_handler = GetArticleBySlugHandler(read_repository)
    
    result = await read_repository.find_by_slug(command.title.lower().replace(" ", "-"))
    return result


@router.get("/articles", response_model=List[schemas.ArticleResponse])
async def list_articles(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    repository = SqlAlchemyArticleReadRepository(db)
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
            "status": a.status,
            "preview_url": a.preview_url,
        }
        for a in articles
    ]


@router.get("/articles/{slug}", response_model=schemas.ArticleResponse)
async def get_article(slug: str, db: AsyncSession = Depends(get_db)):
    repository = SqlAlchemyArticleReadRepository(db)
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
        "status": article.status,
        "preview_url": article.preview_url,
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
    
    read_repository = SqlAlchemyArticleReadRepository(db)
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


@router.post("/articles/{article_id}/publish", status_code=status.HTTP_202_ACCEPTED)
async def publish_article(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
    task_producer: ITaskProducer = Depends(get_task_producer)
):
    """
    Запустить процесс публикации статьи (начало SAGA).
    Доступен только автору статьи и только для статей в статусе DRAFT.
    
    После вызова статья переходит в статус PENDING_PUBLISH и отправляется на модерацию.
    """
    repository = SqlAlchemyArticleWriteRepository(db)
    handler = PublishArticleHandler(repository, task_producer)
    
    command = PublishArticleCommand(
        article_id=article_id,
        user_id=current_user.id
    )
    
    try:
        result = await handler.handle(command)
    except ArticleNotFoundException:
        raise HTTPException(status_code=404, detail="Article not found")
    except NotAuthorizedToModifyArticleException:
        raise HTTPException(status_code=403, detail="Not authorized to publish this article")
    except ArticleNotInDraftException:
        raise HTTPException(status_code=400, detail="Article must be in DRAFT status to publish")
    
    return result
