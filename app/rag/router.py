import json
from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import SessionDep
from app.rag.dependencies import (
    OpenSearchVectorStore,
    OpenSearchVectorStoreLangChain,
    QDrantVectorStore,
    get_os_vector_store,
    get_os_vector_store_langchain,
    get_qdrant_vector_store,
)
from app.rag.models import ConversationData, ConversationForm, ConversationInput
from app.rag.utils import add_conversation
from app.users.dependencies import get_current_user
from app.users.models import UserData

router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
)


@router.post("/qdrant")
async def chat_qdrant(
    input_conversation: ConversationInput,
    qdrant_vector_store: Annotated[QDrantVectorStore, Depends(get_qdrant_vector_store)],
):
    response = qdrant_vector_store.similarity_search(input_conversation.query)
    return response


@router.post("/open-search")
async def chat_open_search(
    input_conversation: ConversationInput,
    os_vector_store: Annotated[OpenSearchVectorStore, Depends(get_os_vector_store)],
):
    response = os_vector_store.search_documents(input_conversation.query)
    return response


@router.post("/open-search-langchain")
async def chat_open_search_langchain(
    input_conversation: ConversationInput,
    os_vector_store_langchain: Annotated[
        OpenSearchVectorStoreLangChain,
        Depends(get_os_vector_store_langchain),
    ],
    db: SessionDep,
    current_user: Annotated[UserData, Depends(get_current_user)],
    response_model=ConversationData,
):
    response = json.loads(
        await os_vector_store_langchain.rag(input_conversation.query)
    )["content"]
    conversation_form = ConversationForm(
        query=input_conversation.query, response=response
    )
    added_conversation = add_conversation(db, conversation_form, current_user.id)
    return added_conversation
