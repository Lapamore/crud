from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import os

from modules.articles.api import router as articles_router
from modules.comments.api import router as comments_router

app = FastAPI(
    title="Blog Platform API",
    description="A simple blog platform API.",
    version="1.0.0",
    root_path=os.getenv("ROOT_PATH", "")
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

app.include_router(articles_router, prefix="/api", tags=["Articles"])
app.include_router(comments_router, prefix="/api", tags=["Comments"])
