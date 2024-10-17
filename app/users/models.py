from pydantic import BaseModel
from sqlmodel import Field, SQLModel


# User
class UserBase(SQLModel):
    username: str = Field(index=True)


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    is_active: bool = Field(default=False)


class UserForm(UserBase):
    password: str


class UserCreate(UserBase):
    hashed_password: str


class UserData(UserBase):
    id: int
    is_active: bool


# Token
class TokenEncode(BaseModel):
    access_token: str
    token_type: str


class TokenDecode(BaseModel):
    username: str
