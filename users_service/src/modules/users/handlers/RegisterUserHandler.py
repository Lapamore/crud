from ..commands import RegisterUserCommand
from ..repositories.core import IUserWriteRepository
from ..exceptions import EmailAlreadyExistsException, UsernameAlreadyExistsException
from core.auth import get_password_hash


class RegisterUserHandler:
    def __init__(self, repository: IUserWriteRepository):
        self._repository = repository

    async def handle(self, command: RegisterUserCommand) -> int:
        existing_user = await self._repository.find_by_email(command.email)
        if existing_user:
            raise EmailAlreadyExistsException(command.email)

        existing_user = await self._repository.find_by_username(command.username)
        if existing_user:
            raise UsernameAlreadyExistsException(command.username)

        hashed_password = get_password_hash(command.password)

        user_id = await self._repository.create(
            email=command.email,
            username=command.username,
            hashed_password=hashed_password,
            bio=command.bio,
            image_url=command.image_url,
        )

        return user_id
