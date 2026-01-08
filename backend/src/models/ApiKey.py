import sqlalchemy as sa
from datetime import datetime
from database import Base

__all__ = ["ApiKey"]


class ApiKey(Base):
    """
    Модель для хранения внутренних API-ключей для service-to-service коммуникаций.
    """
    __tablename__ = "api_keys"
    __table_args__ = {'extend_existing': True}

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    key = sa.Column(sa.String(128), unique=True, index=True, nullable=False)
    description = sa.Column(sa.String(255), nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = sa.Column(sa.DateTime, nullable=True)  # null = never expires
    is_active = sa.Column(sa.Boolean, default=True, nullable=False)
