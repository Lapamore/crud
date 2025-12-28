from datetime import timedelta
from typing import Tuple

from ..commands import LoginCommand
from ..repositories.core import IUserReadRepository
from ..exceptions import InvalidCredentialsException
from core.auth import verify_password, create_access_token


class LoginHandler:
    def __init__(self, repository: IUserReadRepository):
        self._repository = repository

    async def handle(self, command: LoginCommand) -> Tuple[str, str]:
        """Returns (access_token, token_type)."""
        user = await self._repository.find_by_username(command.username)
        if not user:
            raise InvalidCredentialsException()

        if not verify_password(command.password, user.hashed_password):
            raise InvalidCredentialsException()

        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.username, "id": user.id},
            expires_delta=access_token_expires,
        )

        return access_token, "bearer"
