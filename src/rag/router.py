from fastapi import APIRouter, WebSocket

from src.rag.handlers.similarity_searcher import get_similarity_searcher


router = APIRouter(prefix="/rag", tags=["RAG"])


@router.websocket("/chat-similarity-searcher")
async def chat_similarity_searcher(websocket: WebSocket):
    similarity_searcher = get_similarity_searcher()
    await websocket.accept()
    while True:
        text = await websocket.receive_text()
        response = similarity_searcher.similarity_search(text)
        await websocket.send_text(f"Response: {response}")
