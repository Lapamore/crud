from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class UpdateUserCommand:
    user_id: int
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    bio: Optional[str] = None
    image_url: Optional[str] = None
