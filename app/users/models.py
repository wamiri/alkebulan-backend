import uuid
from typing import TYPE_CHECKING

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.rag.models import Conversation


# User
class UserBase(SQLModel):
    username: str = Field(index=True)


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    is_active: bool = Field(default=False)

    conversations: list["Conversation"] = Relationship(back_populates="user")


class UserForm(UserBase):
    password: str


class UserCreate(UserBase):
    hashed_password: str


class UserData(UserBase):
    id: uuid.UUID
    is_active: bool


# Token
class TokenEncode(BaseModel):
    access_token: str
    token_type: str


class TokenDecode(BaseModel):
    username: str
