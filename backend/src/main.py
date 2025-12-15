import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka, FastapiProvider

from core.providers import DatabaseProvider
from modules.articles.ArticlesApp import ArticlesApp
from modules.articles.web.ArticleRouter import ArticleRouter
from modules.comments.CommentsApp import CommentsApp
from modules.comments.web.CommentRouter import CommentRouter


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await app.state.dishka_container.close()


app = FastAPI(
    title="Blog Platform API",
    description="A simple blog platform API.",
    version="1.0.0",
    root_path=os.getenv("ROOT_PATH", ""),
    lifespan=lifespan
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "backend"}


@app.get("/")
def read_root():
    return {"message": "Welcome to the Blog API"}


container = make_async_container(
    DatabaseProvider(),
    ArticlesApp()(),
    CommentsApp()(),
    FastapiProvider()
)
setup_dishka(container, app)

article_router = ArticleRouter()
article_router(app)

comment_router = CommentRouter()
comment_router(app)
