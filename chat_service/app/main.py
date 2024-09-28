import os

from app.config import APP_URL
from app.utils import get_similarity_searcher
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse


app = FastAPI(redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/chat-similarity-searcher")
async def chat_similarity_searcher(websocket: WebSocket):
    similarity_searcher = get_similarity_searcher()
    await websocket.accept()
    while True:
        text = await websocket.receive_text()
        response = similarity_searcher.similarity_search(text)
        await websocket.send_text(f"Response: {response}")


@app.get("/chat-similarity-searcher-html")
async def chat_similarity_searcher_HTML():
    web_socket_url = f"ws://{APP_URL}/chat-similarity-searcher"
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
