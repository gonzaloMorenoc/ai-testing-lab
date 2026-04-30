from __future__ import annotations

import asyncio
import json
import socket
import threading
import time
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse

_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>Mock Chat</title></head>
<body>
  <div id="messages"></div>
  <input id="input" type="text" placeholder="Type a message…" />
  <button id="send">Send</button>
  <div id="response" data-complete="false"></div>
  <script>
    document.getElementById('send').addEventListener('click', async () => {
      const input = document.getElementById('input');
      const msg = input.value.trim();
      const messagesEl = document.getElementById('messages');
      const responseEl = document.getElementById('response');

      if (!msg) {
        messagesEl.textContent = 'Error: empty input';
        return;
      }

      messagesEl.textContent = '';
      responseEl.textContent = '';
      responseEl.setAttribute('data-complete', 'false');

      const res = await fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: msg}),
      });

      const reader = res.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const {done, value} = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, {stream: true});
        for (const line of chunk.split('\\n')) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            if (data.done) {
              responseEl.setAttribute('data-complete', 'true');
            } else if (data.token !== undefined) {
              responseEl.textContent += data.token;
            }
          }
        }
      }
    });
  </script>
</body>
</html>
"""

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    """Devuelve el HTML del chatbot con un input, botón de envío y div de respuesta."""
    return HTMLResponse(_HTML)


@app.post("/chat")
async def chat(request: Request) -> StreamingResponse:
    """Acepta {message: str} y emite tokens SSE: data: {"token": "..."} + data: {"done": true}."""
    body = await request.json()
    message: str = body.get("message", "")

    async def generate() -> AsyncIterator[str]:
        """Genera tokens palabra a palabra con delay de 50ms para simular streaming LLM."""
        words = f"Echo: {message}".split()
        for word in words:
            yield f"data: {json.dumps({'token': word + ' '})}\n\n"
            await asyncio.sleep(0.05)
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


def start_server(port: int) -> threading.Thread:
    """Inicia el servidor FastAPI en un hilo daemon y espera hasta que el puerto esté disponible."""
    import uvicorn

    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    for _ in range(30):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return thread
        time.sleep(0.1)

    raise RuntimeError(f"Server did not start on port {port} after 3 seconds")
