from abc import ABC, abstractmethod

class ISubscriberWriteRepository(ABC):
    @abstractmethod
    async def subscribe(self, subscriber_id: int, author_id: int) -> None:
        pass
