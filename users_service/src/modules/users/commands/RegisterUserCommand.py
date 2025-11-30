from typing import Optional
from pydantic import BaseModel, ConfigDict


class RegisterUserCommand(BaseModel):
    model_config = ConfigDict(frozen=True)

    email: str
    username: str
    password: str
    bio: Optional[str] = None
    image_url: Optional[str] = None
