from fastapi import APIRouter, Depends, WebSocket
from fastapi.responses import HTMLResponse

from app.chat.config import APP_URL
from app.chat.utils import get_open_searcher, get_similarity_searcher

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
    responses={401: {"description": "Unauthorized"}},
)


@router.websocket("/similarity-searcher")
async def chat_similarity_searcher(websocket: WebSocket):
    similarity_searcher = get_similarity_searcher()
    await websocket.accept()
    while True:
        text = await websocket.receive_text()
        response = similarity_searcher.similarity_search(text)
        await websocket.send_text(f"Response: {response}")


@router.websocket("/open-searcher")
async def chat_open_search(websocket: WebSocket):
    open_searcher = get_open_searcher()
    await websocket.accept()
    while True:
        text = await websocket.receive_text()
        response = open_searcher.search_documents(text)
        await websocket.send_text(f"Response: {response}")
