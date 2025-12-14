from ..commands.SubscribeCommand import SubscribeCommand
from ..repositories.core.ISubscriberWriteRepository import ISubscriberWriteRepository

class SubscribeHandler:
    def __init__(self, repository: ISubscriberWriteRepository):
        self._repository = repository

    async def handle(self, command: SubscribeCommand) -> None:
        await self._repository.subscribe(command.subscriber_id, command.target_user_id)
