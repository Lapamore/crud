from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .routes import articles, users, comments

app = FastAPI(
    title="Blog Platform API",
    description="A simple blog platform API.",
    version="1.0.0"
)

# Custom exception handlers
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


@app.get("/")
def read_root():
    return {"message": "Welcome to the Blog API"}

# Include routers
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(articles.router, prefix="/api", tags=["Articles"])
app.include_router(comments.router, prefix="/api", tags=["Comments"])
