from ..commands.UpdateSubscriptionKeyCommand import UpdateSubscriptionKeyCommand
from ..repositories.core.IUserWriteRepository import IUserWriteRepository

class UpdateSubscriptionKeyHandler:
    def __init__(self, repository: IUserWriteRepository):
        self._repository = repository

    async def handle(self, command: UpdateSubscriptionKeyCommand) -> None:
        await self._repository.update_subscription_key(command.user_id, command.subscription_key)
