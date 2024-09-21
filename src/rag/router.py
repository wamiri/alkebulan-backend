from fastapi import APIRouter, Depends, UploadFile, WebSocket

from src.context.query_engine import get_query_engine
from src.rag.utils.file_readers import read_file
from src.rag.utils.file_uploaders import upload_file
from src.rag.utils.workflow import run_workflow

router = APIRouter(prefix="/rag", tags=["rag"])


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


@router.websocket("/chat")
async def chat(websocket: WebSocket):
    query_engine = get_query_engine() 
    await websocket.accept()
    while True:
        text = await websocket.receive_text()
        response = query_engine.query(text)
        await websocket.send_text(f"Response: {response}")
