from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.chat.router import router as chat_router
from app.users.router import router as users_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users_router)
app.include_router(chat_router)


@app.get("/ws-docs", tags=["Docs"])
async def ws_docs():
    return FileResponse("./docs/ws-docs.html")
