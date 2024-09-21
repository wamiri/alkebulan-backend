from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from src.rag.router import router as rag_router

app = FastAPI(docs_url="/api", redoc_url=None)
app.include_router(rag_router)


@app.get("/")
async def main():
    content = """
    <body>
    <form action="/rag/upload" enctype="multipart/form-data" method="post">
    <input name="upload_files" type="file" multiple>
    <input type="submit">
    </form>
    </body>
    """
    return HTMLResponse(content=content)
