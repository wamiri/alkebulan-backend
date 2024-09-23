from fastapi import APIRouter, UploadFile, WebSocket

from src.rag.handlers.file_readers import read_file
from src.rag.handlers.file_uploaders import upload_file
from src.rag.handlers.workflow import run_workflow
from src.utils.query_engine import get_query_engine
from src.utils.similarity_searcher import get_similarity_searcher

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/upload")
async def upload(upload_files: list[UploadFile]):
    query_engine = get_query_engine()
    documents = list()
    for file in upload_files:
        bytes_data = await file.read()
        filename, file_extension = await upload_file(bytes_data, file.filename)
        documents += await read_file(filename, file_extension)

    query_engine.set_engine(await run_workflow(documents))
    return "Query engine loaded"


@router.websocket("/chat-query-engine")
async def chat_query_engine(websocket: WebSocket):
    query_engine = get_query_engine()
    await websocket.accept()
    while True:
        text = await websocket.receive_text()
        response = query_engine.query(text)
        await websocket.send_text(f"Response: {response}")


@router.websocket("/chat-similarity-searcher")
async def chat_similarity_searcher(websocket: WebSocket):
    similarity_searcher = get_similarity_searcher()
    await websocket.accept()
    while True:
        text = await websocket.receive_text()
        response = similarity_searcher.similarity_search(text)
        await websocket.send_text(f"Response: {response}")
