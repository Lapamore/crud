from fastapi import FastAPI
from .routes import users

app = FastAPI(
    title="Users API",
    description="A separate service for managing users.",
    version="1.0.0"
)

@app.get("/api")
def read_root():
    return {"message": "Welcome to the Users API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "users-api"}

app.include_router(users.router, prefix="/api", tags=["Users"])