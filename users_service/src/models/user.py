import sqlalchemy as sa
from ..database import Base


class User(Base):
    __tablename__ = "users"
    
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    email = sa.Column(sa.String, unique=True, index=True, nullable=False)
    username = sa.Column(sa.String, unique=True, index=True, nullable=False)
    hashed_password = sa.Column(sa.String, nullable=False)
    bio = sa.Column(sa.String, nullable=True)
    image_url = sa.Column(sa.String, nullable=True)