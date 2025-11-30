from typing import Optional

from ..queries import GetUserByEmailQuery
from ..repositories.core import IUserReadRepository
from ..dto import UserDTO


class GetUserByEmailHandler:
    def __init__(self, repository: IUserReadRepository):
        self._repository = repository

    async def handle(self, query: GetUserByEmailQuery) -> Optional[UserDTO]:
        return await self._repository.find_by_email(query.email)
