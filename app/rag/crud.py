import uuid

from sqlmodel import select

from app.dependencies import SessionDep
from app.rag.models import Conversation, ConversationCreate


def create_conversation(db: SessionDep, conversation_create: ConversationCreate):
    db_conversation = Conversation.model_validate(conversation_create)
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation


def get_conversations_by_user_id(db: SessionDep, user_id: uuid.UUID):
    statement = select(Conversation).where(Conversation.user_id == user_id)
    found_conversations = db.exec(statement)
    return found_conversations
