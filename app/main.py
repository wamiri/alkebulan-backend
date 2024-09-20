from typing import Union

from fastapi import FastAPI

from .routers import rag

app = FastAPI(docs_url=None, redoc_url="/api")
app.include_router(rag.router)


@app.get("/")
def hello():
    return "Hello, world!"
