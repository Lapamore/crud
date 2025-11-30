from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class UserDTO:
    id: int
    email: str
    username: str
    hashed_password: str
    bio: Optional[str] = None
    image_url: Optional[str] = None
