import uuid

from sqlmodel import Field, Relationship, SQLModel

from app.users.models import User


class ConversationInput(SQLModel):
    query: str


class ConversationBase(ConversationInput):
    response: str


class Conversation(ConversationBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    user_id: uuid.UUID = Field(default=None, foreign_key="user.id")
    user: User | None = Relationship(back_populates="conversations")


class ConversationForm(ConversationBase):
    pass


class ConversationCreate(ConversationBase):
    user_id: uuid.UUID


class ConversationData(ConversationBase):
    id: uuid.UUID
