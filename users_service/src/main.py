from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import os

from .modules.users.api import router as users_router

app = FastAPI(
    title="Users API",
    description="Microservice for user management and authentication.",
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
    return {"status": "healthy", "service": "users-api"}


@app.get("/")
def read_root():
    return {"message": "Welcome to the Users API"}


app.include_router(users_router, prefix="/api", tags=["Users"])

@app.on_event("startup")
async def startup_event():
    print("Listing all routes:")
    for route in app.routes:
        if hasattr(route, "path"):
            print(f"Route: {route.path} {route.methods}")
