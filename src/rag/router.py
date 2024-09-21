from fastapi import APIRouter, UploadFile

from src.rag.utils.file_readers import read_file
from src.rag.utils.file_uploaders import upload_file
from src.rag.utils.workflow import run_workflow

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/upload")
async def upload(upload_files: list[UploadFile]):
    documents = list()
    for file in upload_files:
        bytes_data = await file.read()
        filename, file_extension = await upload_file(bytes_data, file.filename)
        documents += await read_file(filename, file_extension)

    query_engine = await run_workflow(documents)
    return "Query engine loaded" if query_engine is not None else "No query engine"


@router.get("/chat")
async def chat():
    return "Chatting..."
