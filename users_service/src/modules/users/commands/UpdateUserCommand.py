from typing import Optional
from pydantic import BaseModel, ConfigDict


class UpdateUserCommand(BaseModel):
    model_config = ConfigDict(frozen=True)

    user_id: int
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    bio: Optional[str] = None
    image_url: Optional[str] = None
