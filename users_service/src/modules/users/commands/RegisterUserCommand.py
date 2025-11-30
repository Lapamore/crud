from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RegisterUserCommand:
    email: str
    username: str
    password: str
    bio: Optional[str] = None
    image_url: Optional[str] = None
