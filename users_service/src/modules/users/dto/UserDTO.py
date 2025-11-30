from typing import Optional
from pydantic import BaseModel, ConfigDict


class UserDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    email: str
    username: str
    hashed_password: str
    bio: Optional[str] = None
    image_url: Optional[str] = None
