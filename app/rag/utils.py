import uuid

from app.dependencies import SessionDep
from app.rag.crud import create_conversation
from app.rag.models import ConversationCreate, ConversationData, ConversationForm


def add_conversation(
    db: SessionDep,
    conversation_form: ConversationForm,
    user_id: uuid.UUID,
):
    conversation_create = ConversationCreate(
        query=conversation_form.query,
        response=conversation_form.response,
        user_id=user_id,
    )
    created_conversation = create_conversation(db, conversation_create)
    conversation_data = ConversationData(
        query=created_conversation.query,
        response=created_conversation.response,
        id=created_conversation.id,
    )

    return conversation_data
