from fastapi import APIRouter

router = APIRouter(prefix="/rag", tags=["rag"])


@router.get("/upload")
async def upload():
    return "Uploading files"


@router.get("/chat")
async def chat():
    return "Chatting..."
