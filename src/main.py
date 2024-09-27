import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from src.rag.router import router as rag_router

APP_URL = os.environ.get("APP_URL", "localhost:8000")
app = FastAPI(docs_url="/api", redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(rag_router)


@app.get("/", tags=["Hello"])
async def hello():
    return "Hello, world."


@app.get("/chat-similarity-searcher", tags=["Similarity Searcher"])
async def chat_similarity_searcher():
    web_socket_url = f"ws://{APP_URL}/rag/chat-similarity-searcher"
    html = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>Chat</title>
        </head>
        <body>
            <h1>WebSocket Chat</h1>
            <form action="" onsubmit="sendMessage(event)">
                <input type="text" id="messageText" autocomplete="off"/>
                <button>Send</button>
            </form>
            <ul id='messages'>
            </ul>
            <script>
                var ws = new WebSocket("{web_socket_url}");
                ws.onmessage = function(event) {{
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                }};

                function sendMessage(event) {{
                    var input = document.getElementById("messageText")
                    ws.send(input.value)
                    input.value = ''
                    event.preventDefault()
                }}
            </script>
        </body>
    </html>
    """
    return HTMLResponse(html)
