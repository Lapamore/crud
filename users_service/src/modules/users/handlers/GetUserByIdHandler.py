from typing import Optional

from ..queries import GetUserByIdQuery
from ..repositories.core import IUserReadRepository
from ..dto import UserDTO


class GetUserByIdHandler:
    def __init__(self, repository: IUserReadRepository):
        self._repository = repository

    async def handle(self, query: GetUserByIdQuery) -> Optional[UserDTO]:
        return await self._repository.find_by_id(query.user_id)
