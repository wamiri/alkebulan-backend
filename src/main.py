from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from src.rag.router import router as rag_router

app = FastAPI(docs_url="/api", redoc_url=None)
app.include_router(rag_router)


@app.get("/")
async def main():
    html = """
    <body>
    <form action="/rag/upload" enctype="multipart/form-data" method="post">
    <input name="upload_files" type="file" multiple>
    <input type="submit">
    </form>
    </body>
    """
    return HTMLResponse(html)

@app.get("/message")
async def messages():
    html = """
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
                var ws = new WebSocket("ws://localhost:8000/rag/chat");
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                };

                function sendMessage(event) {
                    var input = document.getElementById("messageText")
                    ws.send(input.value)
                    input.value = ''
                    event.preventDefault()
                }
            </script>
        </body>
    </html>
    """
    return HTMLResponse(html)