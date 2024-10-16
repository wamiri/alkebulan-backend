import json

from typing import Annotated
from fastapi import APIRouter, Depends, WebSocket
from fastapi.responses import HTMLResponse

from app.rag.config import APP_URL
from app.rag.dependencies import (
    OpenSearchVectorStore,
    OpenSearchVectorStoreLangChain,
    QDrantVectorStore,
    get_os_vector_store,
    get_os_vector_store_langchain,
    get_qdrant_vector_store,
)

router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
)


@router.websocket("/qdrant")
async def chat_qdrant(
    websocket: WebSocket,
    qdrant_vector_store: Annotated[QDrantVectorStore, Depends(get_qdrant_vector_store)],
):
    await websocket.accept()
    while True:
        text = await websocket.receive_text()
        response = qdrant_vector_store.similarity_search(text)
        await websocket.send_text(f"{response}")


@router.get("/qdrant")
async def qdrant():
    """
    ### WebSocket: `{baseURL}/rag/qdrant`

    - **Description**: This WebSocket connects to a Qdrant vector store containing a book on winter sports.
    - **Actions**: Through this connection, you can perform similarity searches and retrieve information from the QDrant vector store.
    """


@router.websocket("/open-search")
async def chat_open_search(
    websocket: WebSocket,
    os_vector_store: Annotated[OpenSearchVectorStore, Depends(get_os_vector_store)],
):
    await websocket.accept()
    while True:
        text = await websocket.receive_text()
        response = os_vector_store.search_documents(text)
        await websocket.send_text(f"{response}")


@router.get("/open-search")
async def open_search():
    """
    ### WebSocket: `{baseURL}/rag/open-search`

    - **Description**: This WebSocket connects to the Amazon OpenSearch instance using the openseach-py client.
    - **Actions**: Through this connection, you can perform similarity searches and retrieve information from the OpenSearch vector store.
    """


@router.websocket("/open-search-langchain")
async def chat_open_search_langchain(
    websocket: WebSocket,
    os_vector_store_langchain: Annotated[
        OpenSearchVectorStoreLangChain,
        Depends(get_os_vector_store_langchain),
    ],
):
    await websocket.accept()
    while True:
        text = await websocket.receive_text()
        response = json.loads(os_vector_store_langchain.rag(text))
        reply = response["content"]
        await websocket.send_text(reply)


@router.get("/open-search-langchain")
async def open_search_langchain():
    """
    ### WebSocket: `{baseURL}/rag/open-search-langchain`

    - **Description**: This WebSocket connects to the Amazon OpenSearch indices: _new_finance_data_ and _ngx_tables_ via LangChain.
    - **Actions**: Through this connection, you can interact with a RAG pipeline that uses the vector stores as retrievers, reranks the results and outputs the response via an LLM.
    """
