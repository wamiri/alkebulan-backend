from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.ingest.router import router as ingest_router
from app.rag.router import router as rag_router
from app.users.router import router as users_router

app = FastAPI(title="Alkebulan Backend API Specification")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest_router)
app.include_router(rag_router)
app.include_router(users_router)
