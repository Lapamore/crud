from dataclasses import dataclass


@dataclass(frozen=True)
class GetUserByIdQuery:
    user_id: int
