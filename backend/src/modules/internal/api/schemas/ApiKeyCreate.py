from pydantic import BaseModel


class ApiKeyCreate(BaseModel):
    description: str
