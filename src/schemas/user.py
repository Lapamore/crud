from typing import Optional, List
from pydantic import BaseModel, EmailStr


# Base schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    bio: Optional[str] = None
    image_url: Optional[str] = None


# Schema for user creation (registration)
class UserCreate(UserBase):
    password: str


# Schema for user update
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    bio: Optional[str] = None
    image_url: Optional[str] = None


# Schema for representing a user in the database (includes hashed password)
class UserInDB(UserBase):
    id: int
    hashed_password: str

    class Config:
        from_attributes = True


# Public user schema (what is returned from API)
class User(UserBase):
    id: int

    class Config:
        from_attributes = True


# Schema for token response
class Token(BaseModel):
    access_token: str
    token_type: str


# Schema for data inside the token
class TokenData(BaseModel):
    username: Optional[str] = None
