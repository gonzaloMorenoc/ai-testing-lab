"""
Solución módulo 11: mock_chat_server con spinner CSS.
"""
from __future__ import annotations

import asyncio
import json
import socket
import threading
import time
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse

_HTML_WITH_SPINNER = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"><title>Mock Chat With Spinner</title>
  <style>
    #spinner { display: none; }
    #spinner.active { display: inline-block; }
  </style>
</head>
<body>
  <div id="messages"></div>
  <input id="input" type="text" placeholder="Type a message…" />
  <button id="send">Send</button>
  <span id="spinner" aria-label="loading">⏳</span>
  <div id="response" data-complete="false"></div>
  <script>
    document.getElementById('send').addEventListener('click', async () => {
      const input = document.getElementById('input');
      const msg = input.value.trim();
      const messagesEl = document.getElementById('messages');
      const responseEl = document.getElementById('response');
      const spinner = document.getElementById('spinner');

      if (!msg) { messagesEl.textContent = 'Error: empty input'; return; }

      messagesEl.textContent = '';
      responseEl.textContent = '';
      responseEl.setAttribute('data-complete', 'false');
      spinner.classList.add('active');

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
              spinner.classList.remove('active');
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
    return HTMLResponse(_HTML_WITH_SPINNER)


@app.post("/chat")
async def chat(request: Request) -> StreamingResponse:
    body = await request.json()
    message: str = body.get("message", "")

    async def generate() -> AsyncIterator[str]:
        for word in f"Echo: {message}".split():
            yield f"data: {json.dumps({'token': word + ' '})}\n\n"
            await asyncio.sleep(0.05)
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


def start_server(port: int) -> threading.Thread:
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
    return thread


if __name__ == "__main__":
    print("Run with pytest-playwright to see the spinner test.")
    print("Example test:\n")
    print("  page.fill('#input', 'hello')")
    print("  page.click('#send')")
    print("  expect(page.locator('#spinner')).to_have_class('active')")
    print("  expect(page.locator('#response')).to_have_attribute('data-complete', 'true')")
    print("  expect(page.locator('#spinner')).not_to_have_class('active')")
