from pydantic import BaseModel
from typing import List
from .ApiKeyResponse import ApiKeyResponse


class InitKeysResponse(BaseModel):
    message: str
    keys: List[ApiKeyResponse]
