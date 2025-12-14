from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from .....models import Subscriber
from ..core.ISubscriberWriteRepository import ISubscriberWriteRepository


class SqlAlchemySubscriberWriteRepository(ISubscriberWriteRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def subscribe(self, subscriber_id: int, author_id: int) -> None:
        subscriber = Subscriber(subscriber_id=subscriber_id, author_id=author_id)
        self._session.add(subscriber)
        try:
            await self._session.commit()
        except IntegrityError:
            await self._session.rollback()
            pass
