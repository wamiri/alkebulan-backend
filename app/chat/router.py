from fastapi import APIRouter, Depends, WebSocket
from fastapi.responses import HTMLResponse

from app.chat.config import APP_URL
from app.chat.utils import (
    get_os_vector_store,
    get_os_vector_store_langchain,
    get_qdrant_vector_store,
)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
    responses={401: {"description": "Unauthorized"}},
)


@router.websocket("/qdrant")
async def chat_qdrant(websocket: WebSocket):
    qdrant_vector_store = get_qdrant_vector_store()
    await websocket.accept()
    while True:
        text = await websocket.receive_text()
        response = qdrant_vector_store.similarity_search(text)
        await websocket.send_text(f"Response: {response}")


@router.websocket("/open-search")
async def chat_open_search(websocket: WebSocket):
    os_vector_store = get_os_vector_store()
    await websocket.accept()
    while True:
        text = await websocket.receive_text()
        response = os_vector_store.search_documents(text)
        await websocket.send_text(f"Response: {response}")


@router.websocket("/open-search-langchain")
async def chat_open_search_langchain(websocket: WebSocket):
    os_vector_store_langchain = get_os_vector_store_langchain()
    await websocket.accept()
    while True:
        text = await websocket.receive_text()
        response = os_vector_store_langchain.rag(text)
        await websocket.send_text(f"Response: {response}")
