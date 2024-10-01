from pydantic import BaseModel


class TokenEncode(BaseModel):
    access_token: str
    token_type: str


class TokenDecode(BaseModel):
    username: str | None = None


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserData(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
