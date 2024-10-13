from app.rag.utils import (
    OpenSearchVectorStore,
    OpenSearchVectorStoreLangChain,
    QDrantVectorStore,
)


def get_os_vector_store():
    os_vector_store = OpenSearchVectorStore()
    return os_vector_store


def get_os_vector_store_langchain():
    os_vector_store_langchain = OpenSearchVectorStoreLangChain()
    return os_vector_store_langchain


def get_qdrant_vector_store():
    qdrant_vector_store = QDrantVectorStore()
    return qdrant_vector_store
