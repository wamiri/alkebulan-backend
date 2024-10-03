from fastapi import APIRouter, Depends, WebSocket
from fastapi.responses import HTMLResponse

from app.chat.config import APP_URL
from app.chat.utils import get_open_searcher, get_rag_chain, get_similarity_searcher

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
    responses={401: {"description": "Unauthorized"}},
)


@router.websocket("/similarity-search")
async def chat_similarity_searcher(websocket: WebSocket):
    similarity_searcher = get_similarity_searcher()
    await websocket.accept()
    while True:
        text = await websocket.receive_text()
        response = similarity_searcher.similarity_search(text)
        await websocket.send_text(f"Response: {response}")


@router.websocket("/open-search")
async def chat_open_search(websocket: WebSocket):
    open_searcher = get_open_searcher()
    await websocket.accept()
    while True:
        text = await websocket.receive_text()
        response = open_searcher.search_documents(text)
        await websocket.send_text(f"Response: {response}")


@router.websocket("/rag-chain")
async def chat_rag_chain(websocket: WebSocket):
    rag_chain = get_rag_chain()
    await websocket.accept()
    while True:
        text = await websocket.receive_text()
        response = rag_chain.invoke(text)
        await websocket.send_text(f"Response: {response}")
