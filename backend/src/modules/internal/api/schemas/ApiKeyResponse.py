from pydantic import BaseModel


class ApiKeyResponse(BaseModel):
    id: int
    key: str
    description: str
    is_active: bool
