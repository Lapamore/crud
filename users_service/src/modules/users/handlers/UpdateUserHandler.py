from ..commands import UpdateUserCommand
from ..repositories.core import IUserWriteRepository
from ..exceptions import UserNotFoundException, EmailAlreadyExistsException, UsernameAlreadyExistsException
from src.core.auth import get_password_hash


class UpdateUserHandler:
    def __init__(self, repository: IUserWriteRepository):
        self._repository = repository

    async def handle(self, command: UpdateUserCommand) -> None:
        user = await self._repository.find_by_id(command.user_id)
        if not user:
            raise UserNotFoundException(user_id=command.user_id)

        if command.email and command.email != user.email:
            existing = await self._repository.find_by_email(command.email)
            if existing:
                raise EmailAlreadyExistsException(command.email)

        if command.username and command.username != user.username:
            existing = await self._repository.find_by_username(command.username)
            if existing:
                raise UsernameAlreadyExistsException(command.username)

        hashed_password = None
        if command.password:
            hashed_password = get_password_hash(command.password)

        await self._repository.update(
            user_id=command.user_id,
            email=command.email,
            username=command.username,
            hashed_password=hashed_password,
            bio=command.bio,
            image_url=command.image_url,
        )
