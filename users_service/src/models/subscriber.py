import sqlalchemy as sa
from database import Base

__all__ = ["Subscriber"]


class Subscriber(Base):
    __tablename__ = "subscribers"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    subscriber_id = sa.Column(sa.BigInteger, nullable=False)
    author_id = sa.Column(sa.BigInteger, nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)

    __table_args__ = (
        sa.UniqueConstraint('subscriber_id', 'author_id', name='ux_sub'),
    )
