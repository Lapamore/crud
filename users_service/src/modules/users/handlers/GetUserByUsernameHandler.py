from typing import Optional

from ..queries import GetUserByUsernameQuery
from ..repositories.core import IUserReadRepository
from ..dto import UserDTO


class GetUserByUsernameHandler:
    def __init__(self, repository: IUserReadRepository):
        self._repository = repository

    async def handle(self, query: GetUserByUsernameQuery) -> Optional[UserDTO]:
        return await self._repository.find_by_username(query.username)
