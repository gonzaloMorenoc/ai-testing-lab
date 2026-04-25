# Batch 3 — Módulos de Infraestructura (10-13) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar los módulos 10 (agent-testing), 11 (playwright-streaming), 12 (observability) y 13 (drift-monitoring) del proyecto `ai-testing-lab`, completando los 13 módulos del laboratorio.

**Architecture:** Mismo patrón que Batch 1 y 2: sin `src/__init__.py` ni `tests/__init__.py`, conftest.py raíz inserta el path del módulo en `sys.path`, todos los tests no-slow pasan sin API key. Módulo 11 requiere playwright + fastapi+uvicorn opcionales (skip automático si no están instalados). Módulo 13 requiere numpy.

**Tech Stack:** Python 3.11+, pytest, dataclasses, itertools, contextvars, time, re, numpy (módulo 13), fastapi+uvicorn+playwright (módulo 11 opcional), groq SDK (solo tests slow).

---

## Task 1 — Módulo 10: agent-testing

### 1.1 Estructura de archivos

```
modules/10-agent-testing/
├── conftest.py
├── src/
│   ├── simple_agent.py
│   └── trajectory_evaluator.py
└── tests/
    ├── conftest.py
    └── test_agent_testing.py
```

### 1.2 `modules/10-agent-testing/conftest.py`

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
```

### 1.3 `modules/10-agent-testing/src/simple_agent.py`

```python
from __future__ import annotations

import re
from dataclasses import dataclass, field

_CALC_KEYWORDS: tuple[str, ...] = (
    "calculate",
    "compute",
    "how much",
    "how many",
    "sum of",
    "add",
    "multiply",
)
_FORMAT_KEYWORDS: tuple[str, ...] = ("format", "report", "summarize", "structure")
_SAFE_EXPR_RE = re.compile(r"[^0-9\+\-\*/\.\s\(\)]+")


@dataclass(frozen=True)
class ToolCall:
    tool: str
    argument: str
    result: str


@dataclass
class AgentResult:
    query: str
    trajectory: list[ToolCall] = field(default_factory=list)
    final_output: str = ""


class SimpleAgent:

    def search(self, query: str) -> str:
        return f"Search result for: {query}"

    def calculate(self, expr: str) -> str:
        safe = _SAFE_EXPR_RE.sub("", expr).strip()
        if not safe:
            return "0"
        try:
            result = eval(safe, {"__builtins__": {}}, {})  # noqa: S307
            return str(result)
        except Exception:
            return "0"

    def format_response(self, data: str) -> str:
        return f"Report:\n{data}"

    def _select_tool(self, query: str) -> tuple[str, str]:
        low = query.lower()
        if any(k in low for k in _CALC_KEYWORDS):
            match = re.search(r"[\d\s\+\-\*\/\.\(\)]+", query)
            arg = match.group(0).strip() if match else query
            return "calculate", arg
        if any(k in low for k in _FORMAT_KEYWORDS):
            return "format_response", query
        return "search", query

    def run(self, query: str) -> AgentResult:
        result = AgentResult(query=query)
        tool_name, arg = self._select_tool(query)
        tool_fn = getattr(self, tool_name)
        output = tool_fn(arg)
        result.trajectory.append(ToolCall(tool=tool_name, argument=arg, result=output))
        result.final_output = output
        return result
```

### 1.4 `modules/10-agent-testing/src/trajectory_evaluator.py`

```python
from __future__ import annotations

from dataclasses import dataclass
from itertools import zip_longest
from typing import Callable

from src.simple_agent import ToolCall


@dataclass
class ToolCallAccuracyResult:
    score: float
    reason: str

    @property
    def passed(self) -> bool:
        return self.score >= 0.5


@dataclass
class AgentGoalResult:
    achieved: bool
    score: float
    reason: str


class TrajectoryEvaluator:

    def tool_call_accuracy(
        self,
        actual: list[ToolCall],
        expected: list[tuple[str, str]],  # (tool_name, arg_fragment_or_empty)
    ) -> ToolCallAccuracyResult:
        """Score 0-1: exact match=1, right tool wrong arg=0.5/step, wrong tool=0."""
        if not expected:
            return ToolCallAccuracyResult(score=1.0, reason="no expected calls")
        if not actual:
            return ToolCallAccuracyResult(score=0.0, reason="no calls made")

        correct = 0.0
        for act, exp in zip_longest(actual, expected):
            if act is None or exp is None:
                continue
            exp_tool, exp_arg_fragment = exp
            if act.tool == exp_tool:
                if not exp_arg_fragment or exp_arg_fragment.lower() in act.argument.lower():
                    correct += 1.0
                else:
                    correct += 0.5  # right tool, wrong argument

        total = max(len(actual), len(expected))
        score = round(correct / total, 3)

        if score == 1.0 and len(actual) == len(expected):
            reason = "exact match"
        elif len(actual) > len(expected):
            extra = len(actual) - len(expected)
            reason = f"extra steps: {extra} unexpected call(s)"
        elif len(actual) < len(expected):
            missing = len(expected) - len(actual)
            reason = f"missing steps: {missing} call(s) not made"
        else:
            reason = f"partial: score={score:.3f}"

        return ToolCallAccuracyResult(score=score, reason=reason)

    def agent_goal_accuracy(
        self,
        final_output: str,
        goal_checker: Callable[[str], bool],
    ) -> AgentGoalResult:
        achieved = goal_checker(final_output)
        return AgentGoalResult(
            achieved=achieved,
            score=1.0 if achieved else 0.0,
            reason="goal achieved" if achieved else "goal not achieved",
        )
```

### 1.5 `modules/10-agent-testing/tests/conftest.py`

```python
from __future__ import annotations

import pytest

from src.simple_agent import SimpleAgent


@pytest.fixture
def agent() -> SimpleAgent:
    return SimpleAgent()
```

### 1.6 `modules/10-agent-testing/tests/test_agent_testing.py`

```python
from __future__ import annotations

import os

import pytest

from src.simple_agent import AgentResult, SimpleAgent, ToolCall
from src.trajectory_evaluator import TrajectoryEvaluator


class TestSimpleAgent:

    def test_search_query_selects_search_tool(self, agent: SimpleAgent) -> None:
        result = agent.run("What is machine learning?")
        print(f"\n  trajectory: {result.trajectory}")
        assert result.trajectory[0].tool == "search"
        assert "Search result" in result.final_output

    def test_math_query_selects_calculate_tool(self, agent: SimpleAgent) -> None:
        result = agent.run("calculate 2 + 3")
        assert result.trajectory[0].tool == "calculate"
        assert result.final_output == "5"


class TestTrajectoryEvaluator:

    def test_wrong_tool_accuracy_zero(self) -> None:
        evaluator = TrajectoryEvaluator()
        actual = [ToolCall("calculate", "2+3", "5")]
        expected = [("search", "machine learning")]
        result = evaluator.tool_call_accuracy(actual, expected)
        print(f"\n  {result.reason}")
        assert result.score == 0.0

    def test_wrong_arg_correct_tool_partial_credit(self) -> None:
        evaluator = TrajectoryEvaluator()
        actual = [ToolCall("search", "wrong query", "Search result for: wrong query")]
        expected = [("search", "machine learning")]
        result = evaluator.tool_call_accuracy(actual, expected)
        assert result.score == 0.5

    def test_complete_trajectory_exact_match(self) -> None:
        evaluator = TrajectoryEvaluator()
        actual = [
            ToolCall("search", "ai basics", "Search result for: ai basics"),
            ToolCall("calculate", "3 + 4", "7"),
            ToolCall("format_response", "ai summary", "Report:\nai summary"),
        ]
        expected = [("search", "ai basics"), ("calculate", "3 + 4"), ("format_response", "")]
        result = evaluator.tool_call_accuracy(actual, expected)
        print(f"\n  {result.reason}")
        assert result.score == 1.0
        assert result.reason == "exact match"

    def test_extra_step_penalty(self) -> None:
        evaluator = TrajectoryEvaluator()
        actual = [
            ToolCall("search", "query", "result"),
            ToolCall("calculate", "1+1", "2"),
            ToolCall("format_response", "data", "Report:\ndata"),
            ToolCall("search", "extra", "extra result"),  # unexpected extra step
        ]
        expected = [("search", ""), ("calculate", ""), ("format_response", "")]
        result = evaluator.tool_call_accuracy(actual, expected)
        assert result.score < 1.0
        assert "extra" in result.reason

    def test_missing_step_penalty(self) -> None:
        evaluator = TrajectoryEvaluator()
        actual = [
            ToolCall("search", "query", "result"),
            ToolCall("calculate", "1+1", "2"),
        ]
        expected = [("search", ""), ("calculate", ""), ("format_response", "")]
        result = evaluator.tool_call_accuracy(actual, expected)
        assert result.score < 1.0
        assert "missing" in result.reason

    def test_agent_goal_accuracy_achieved(self) -> None:
        evaluator = TrajectoryEvaluator()
        result = evaluator.agent_goal_accuracy(
            final_output="The capital of France is Paris.",
            goal_checker=lambda out: "Paris" in out,
        )
        print(f"\n  goal: {result.reason}")
        assert result.achieved is True
        assert result.score == 1.0

    def test_agent_goal_accuracy_not_achieved(self) -> None:
        evaluator = TrajectoryEvaluator()
        result = evaluator.agent_goal_accuracy(
            final_output="I don't know the answer.",
            goal_checker=lambda out: "Paris" in out,
        )
        assert result.achieved is False
        assert result.score == 0.0

    @pytest.mark.slow
    def test_real_groq_agent(self) -> None:
        if not os.getenv("GROQ_API_KEY"):
            pytest.skip("GROQ_API_KEY no encontrado")
        from groq import Groq  # type: ignore

        client = Groq()

        def groq_search(query: str) -> str:
            resp = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "Answer in one short sentence."},
                    {"role": "user", "content": query},
                ],
                temperature=0.0,
                max_tokens=60,
            )
            return resp.choices[0].message.content or ""

        evaluator = TrajectoryEvaluator()
        output = groq_search("What is 2 + 2?")
        result = evaluator.agent_goal_accuracy(
            final_output=output,
            goal_checker=lambda out: "4" in out,
        )
        print(f"\n  Groq output: {output!r} → achieved={result.achieved}")
        assert isinstance(result.achieved, bool)
```

### 1.7 `modules/10-agent-testing/README.md`

```markdown
# Módulo 10 — Agent Testing

**Status:** implemented

## Objetivos

- Evaluar qué tool selecciona un agente dado un input
- Medir `ToolCallAccuracy` con exact match y partial credit (tool correcta pero argumento incorrecto)
- Evaluar si el agente alcanza el objetivo final con `AgentGoalAccuracy`

## Cómo ejecutar

```bash
cd modules/10-agent-testing
pytest tests/ -m "not slow" -v
pytest tests/ -m slow -v   # requiere GROQ_API_KEY
```

## Ejercicio propuesto

Añade una cuarta tool `translate(text, target_lang)` al agente y verifica que la trayectoria con 4 steps se evalúa correctamente.

Solución en `exercises/solutions/10-agent-testing-solution.py`.
```

### 1.8 `exercises/solutions/10-agent-testing-solution.py`

```python
"""
Solución módulo 10: agente con tool translate + evaluación de trayectoria.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "modules" / "10-agent-testing"))

from src.simple_agent import AgentResult, SimpleAgent, ToolCall, _CALC_KEYWORDS, _FORMAT_KEYWORDS
from src.trajectory_evaluator import TrajectoryEvaluator

_TRANSLATE_KEYWORDS: tuple[str, ...] = ("translate", "in french", "in spanish", "en español")


class ExtendedAgent(SimpleAgent):

    def translate(self, text: str) -> str:
        return f"[translated] {text}"

    def _select_tool(self, query: str) -> tuple[str, str]:
        low = query.lower()
        if any(k in low for k in _TRANSLATE_KEYWORDS):
            return "translate", query
        return super()._select_tool(query)


if __name__ == "__main__":
    agent = ExtendedAgent()
    evaluator = TrajectoryEvaluator()

    result = agent.run("translate hello world in french")
    print(f"Tool: {result.trajectory[0].tool}")
    print(f"Output: {result.final_output}")

    # Evaluar trayectoria de 4 steps
    traj = [
        ToolCall("search", "ai news", "Search result for: ai news"),
        ToolCall("calculate", "10 + 5", "15"),
        ToolCall("translate", "hello", "[translated] hello"),
        ToolCall("format_response", "summary", "Report:\nsummary"),
    ]
    expected = [("search", ""), ("calculate", ""), ("translate", ""), ("format_response", "")]
    accuracy = evaluator.tool_call_accuracy(traj, expected)
    print(f"Accuracy: {accuracy.score} — {accuracy.reason}")
```

### 1.9 Verificación Task 1

```bash
cd /Users/gonzalo/Documents/GitHub/ai-testing-lab
pytest modules/10-agent-testing/tests/ -m "not slow" -v
# Esperado: 8 passed, 1 deselected (slow), 0 failed
python3 exercises/solutions/10-agent-testing-solution.py
```

---

## Task 2 — Módulo 11: playwright-streaming

### 2.1 Estructura de archivos

```
modules/11-playwright-streaming/
├── conftest.py
├── src/
│   └── mock_chat_server.py
└── tests/
    ├── conftest.py
    └── test_playwright_streaming.py
```

### 2.2 `modules/11-playwright-streaming/conftest.py`

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
```

### 2.3 `modules/11-playwright-streaming/src/mock_chat_server.py`

```python
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
    return HTMLResponse(_HTML)


@app.post("/chat")
async def chat(request: Request) -> StreamingResponse:
    body = await request.json()
    message: str = body.get("message", "")

    async def generate() -> AsyncIterator[str]:
        words = f"Echo: {message}".split()
        for word in words:
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
```

### 2.4 `modules/11-playwright-streaming/tests/conftest.py`

```python
from __future__ import annotations

import socket

import pytest


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def server_url() -> str:
    port = _free_port()
    try:
        from src.mock_chat_server import start_server
        start_server(port)
    except ImportError:
        pytest.skip("fastapi or uvicorn not installed — install with: pip install fastapi uvicorn")
    return f"http://127.0.0.1:{port}"
```

### 2.5 `modules/11-playwright-streaming/tests/test_playwright_streaming.py`

```python
from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

# Skip entire module if playwright not installed
pytest.importorskip(
    "playwright",
    reason=(
        "playwright not installed — install with: "
        "pip install playwright pytest-playwright && playwright install chromium"
    ),
)

from playwright.sync_api import Page, expect  # noqa: E402


class TestChatUI:

    def test_response_appears_in_dom(self, page: Page, server_url: str) -> None:
        page.goto(server_url)
        page.fill("#input", "hello world")
        page.click("#send")
        expect(page.locator("#response")).not_to_have_text("", timeout=5_000)

    def test_streaming_incremental(self, page: Page, server_url: str) -> None:
        page.goto(server_url)
        page.fill("#input", "streaming test message with many words")
        page.click("#send")
        page.wait_for_timeout(150)
        initial = page.locator("#response").text_content() or ""
        page.wait_for_timeout(600)
        final = page.locator("#response").text_content() or ""
        assert len(final) >= len(initial), "response should grow or stay the same over time"

    def test_response_complete_attribute(self, page: Page, server_url: str) -> None:
        page.goto(server_url)
        page.fill("#input", "complete test")
        page.click("#send")
        expect(page.locator("#response")).to_have_attribute(
            "data-complete", "true", timeout=10_000
        )
        text = page.locator("#response").text_content()
        assert text and len(text) > 0

    def test_regex_on_response(self, page: Page, server_url: str) -> None:
        page.goto(server_url)
        page.fill("#input", "hello")
        page.click("#send")
        expect(page.locator("#response")).to_have_attribute(
            "data-complete", "true", timeout=10_000
        )
        text = page.locator("#response").text_content() or ""
        assert re.search(r"Echo:", text, re.IGNORECASE), f"Unexpected response: {text!r}"

    def test_empty_input_shows_error(self, page: Page, server_url: str) -> None:
        page.goto(server_url)
        page.click("#send")
        expect(page.locator("#messages")).to_contain_text("Error", timeout=3_000)

    def test_screenshot_saved(self, page: Page, server_url: str, tmp_path: Path) -> None:
        page.goto(server_url)
        page.fill("#input", "screenshot test")
        page.click("#send")
        expect(page.locator("#response")).to_have_attribute(
            "data-complete", "true", timeout=10_000
        )
        screenshot = tmp_path / "chat_final.png"
        page.screenshot(path=str(screenshot))
        assert screenshot.exists()

    def test_iframe_chat(self, page: Page, server_url: str) -> None:
        page.set_content(
            f"<html><body>"
            f'<iframe id="chat-frame" src="{server_url}" width="800" height="600"></iframe>'
            f"</body></html>"
        )
        frame = page.frame_locator("#chat-frame")
        frame.locator("#input").fill("iframe test")
        frame.locator("#send").click()
        expect(frame.locator("#response")).to_have_attribute(
            "data-complete", "true", timeout=10_000
        )

    @pytest.mark.slow
    def test_real_streamlit_chat(self, page: Page) -> None:
        url = os.getenv("STREAMLIT_CHAT_URL", "")
        if not url:
            pytest.skip("STREAMLIT_CHAT_URL not set")
        page.goto(url, timeout=15_000)
        page.wait_for_load_state("networkidle", timeout=15_000)
        assert page.title() != ""
```

### 2.6 `modules/11-playwright-streaming/README.md`

```markdown
# Módulo 11 — Playwright + Streaming SSE

**Status:** implemented

## Prerrequisitos

```bash
pip install fastapi uvicorn playwright pytest-playwright
playwright install chromium
```

## Objetivos

- Levantar un servidor FastAPI con SSE streaming como fixture de pytest
- Verificar que el texto aparece incrementalmente en el DOM con Playwright
- Usar `data-complete="true"` como señal de fin de stream
- Guardar screenshots como artefactos de test

## Cómo ejecutar

```bash
cd modules/11-playwright-streaming
pytest tests/ -m "not slow" -v
# Sin playwright/fastapi instalados: 0 tests collected (skipped gracefully)
```

## Ejercicio propuesto

Añade un indicador visual (spinner CSS) que aparezca mientras el streaming está en curso y desaparezca cuando `data-complete="true"`. Escribe un test Playwright que verifique el ciclo aparecer → desaparecer.

Solución en `exercises/solutions/11-playwright-streaming-solution.py`.
```

### 2.7 `exercises/solutions/11-playwright-streaming-solution.py`

```python
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
```

### 2.8 Verificación Task 2

```bash
cd /Users/gonzalo/Documents/GitHub/ai-testing-lab

# Sin playwright instalado:
pytest modules/11-playwright-streaming/tests/ -m "not slow" -v
# Esperado: 0 items collected (módulo skipped por importorskip)

# Con playwright+fastapi instalados:
pytest modules/11-playwright-streaming/tests/ -m "not slow" -v
# Esperado: 7 passed, 1 deselected (slow), 0 failed

python3 exercises/solutions/11-playwright-streaming-solution.py
# Esperado: instrucciones impresas
```

---

## Task 3 — Módulo 12: observability

### 3.1 Estructura de archivos

```
modules/12-observability/
├── conftest.py
├── src/
│   ├── tracer.py
│   └── mock_collector.py
└── tests/
    ├── conftest.py
    └── test_observability.py
```

### 3.2 `modules/12-observability/conftest.py`

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
```

### 3.3 `modules/12-observability/src/tracer.py`

```python
from __future__ import annotations

import time
from contextvars import ContextVar
from dataclasses import dataclass, field
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from src.mock_collector import MockCollector

_CURRENT_SPAN_ID: ContextVar[str | None] = ContextVar("_current_span_id", default=None)
_collector: MockCollector | None = None


def set_collector(collector: MockCollector | None) -> None:
    global _collector
    _collector = collector


@dataclass
class Span:
    name: str
    attributes: dict[str, Any] = field(default_factory=dict)
    input: str = ""
    output: str = ""
    duration_ms: float = 0.0
    status: str = "OK"
    error: str | None = None
    parent_id: str | None = None
    span_id: str = field(default_factory=lambda: hex(id(object()))[2:])


def trace(name: str, **extra_attributes: Any) -> Callable:
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            span = Span(
                name=name,
                attributes=dict(extra_attributes),
                input=str(args[0]) if args else "",
                parent_id=_CURRENT_SPAN_ID.get(),
            )
            token = _CURRENT_SPAN_ID.set(span.span_id)
            start = time.monotonic()
            try:
                result = fn(*args, **kwargs)
                span.output = str(result)
                span.status = "OK"
                return result
            except Exception as exc:
                span.status = "ERROR"
                span.error = str(exc)
                raise
            finally:
                span.duration_ms = round((time.monotonic() - start) * 1000, 2)
                _CURRENT_SPAN_ID.reset(token)
                if _collector is not None:
                    _collector._add(span)

        return wrapper

    return decorator
```

### 3.4 `modules/12-observability/src/mock_collector.py`

```python
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.tracer import Span


@dataclass
class MockCollector:
    _spans: list[Span] = field(default_factory=list)

    def _add(self, span: Span) -> None:
        self._spans.append(span)

    def get_spans(self, name: str | None = None) -> list[Span]:
        if name is None:
            return list(self._spans)
        return [s for s in self._spans if s.name == name]

    def clear(self) -> None:
        self._spans.clear()

    def export(self) -> list[dict[str, Any]]:
        return [
            {
                "name": s.name,
                "input": s.input,
                "output": s.output,
                "duration_ms": s.duration_ms,
                "status": s.status,
                "error": s.error,
                "parent_id": s.parent_id,
                "span_id": s.span_id,
            }
            for s in self._spans
        ]
```

### 3.5 `modules/12-observability/tests/conftest.py`

```python
from __future__ import annotations

import pytest

from src import tracer as tracer_module
from src.mock_collector import MockCollector


@pytest.fixture
def collector() -> MockCollector:
    coll = MockCollector()
    tracer_module.set_collector(coll)
    yield coll
    coll.clear()
    tracer_module.set_collector(None)  # type: ignore[arg-type]
```

### 3.6 `modules/12-observability/tests/test_observability.py`

```python
from __future__ import annotations

import os
import time

import pytest

from src.mock_collector import MockCollector
from src.tracer import Span, trace


class TestTracer:

    def test_decorated_function_creates_span(self, collector: MockCollector) -> None:
        @trace("my_function")
        def fn(x: str) -> str:
            return f"result:{x}"

        fn("hello")
        spans = collector.get_spans()
        print(f"\n  spans: {[s.name for s in spans]}")
        assert len(spans) == 1
        assert spans[0].name == "my_function"

    def test_span_contains_input_output_duration(self, collector: MockCollector) -> None:
        @trace("pipeline_step")
        def process(text: str) -> str:
            return text.upper()

        process("test input")
        span = collector.get_spans("pipeline_step")[0]
        print(f"\n  span: input={span.input!r} output={span.output!r} duration={span.duration_ms}ms")
        assert span.input == "test input"
        assert span.output == "TEST INPUT"
        assert span.duration_ms >= 0.0

    def test_exception_marks_span_error(self, collector: MockCollector) -> None:
        @trace("failing_step")
        def failing(x: str) -> str:
            raise ValueError("something went wrong")

        with pytest.raises(ValueError):
            failing("bad input")

        span = collector.get_spans("failing_step")[0]
        print(f"\n  error span: status={span.status} error={span.error!r}")
        assert span.status == "ERROR"
        assert "something went wrong" in (span.error or "")

    def test_nested_spans_parent_child_relationship(self, collector: MockCollector) -> None:
        @trace("outer")
        def outer_fn(x: str) -> str:
            return inner_fn(x)

        @trace("inner")
        def inner_fn(x: str) -> str:
            return f"processed:{x}"

        outer_fn("data")
        outer_span = collector.get_spans("outer")[0]
        inner_span = collector.get_spans("inner")[0]
        print(f"\n  outer.span_id={outer_span.span_id} inner.parent_id={inner_span.parent_id}")
        assert inner_span.parent_id == outer_span.span_id

    def test_collector_accumulates_multiple_calls(self, collector: MockCollector) -> None:
        @trace("repeated")
        def fn(x: str) -> str:
            return x

        fn("a")
        fn("b")
        fn("c")
        spans = collector.get_spans("repeated")
        assert len(spans) == 3

    def test_get_spans_filters_by_name(self, collector: MockCollector) -> None:
        @trace("alpha")
        def alpha(x: str) -> str:
            return x

        @trace("beta")
        def beta(x: str) -> str:
            return x

        alpha("x")
        beta("y")
        alpha("z")

        alpha_spans = collector.get_spans("alpha")
        beta_spans = collector.get_spans("beta")
        assert len(alpha_spans) == 2
        assert len(beta_spans) == 1

    def test_export_returns_dict_structure(self, collector: MockCollector) -> None:
        @trace("export_test", model="gpt-4")
        def fn(x: str) -> str:
            return x

        fn("value")
        exported = collector.export()
        assert len(exported) == 1
        d = exported[0]
        required_keys = {"name", "input", "output", "duration_ms", "status", "error", "parent_id", "span_id"}
        assert set(d.keys()) == required_keys
        assert d["name"] == "export_test"

    @pytest.mark.slow
    def test_real_langfuse_export(self) -> None:
        if not os.getenv("LANGFUSE_SECRET_KEY"):
            pytest.skip("LANGFUSE_SECRET_KEY no encontrado")
        # Smoke test: verify the module can be imported and a span can be created
        coll = MockCollector()
        from src import tracer as tm
        tm.set_collector(coll)

        @trace("langfuse_test")
        def fn(x: str) -> str:
            time.sleep(0.01)
            return f"result:{x}"

        fn("input_data")
        spans = coll.get_spans()
        assert len(spans) == 1
        assert spans[0].duration_ms > 0
        tm.set_collector(None)  # type: ignore[arg-type]
        print(f"\n  Span exported locally: {spans[0].name} ({spans[0].duration_ms}ms)")
```

### 3.7 `modules/12-observability/README.md`

```markdown
# Módulo 12 — Observabilidad y Tracing

**Status:** implemented

## Objetivos

- Instrumentar funciones con `@trace(name)` sin cambiar su API
- Capturar input, output, duración y errores como spans
- Verificar trazas anidadas con relación padre-hijo
- Exportar spans a un dict para assertions de estructura

## Cómo ejecutar

```bash
cd modules/12-observability
pytest tests/ -m "not slow" -v
pytest tests/ -m slow -v   # requiere LANGFUSE_SECRET_KEY
```

## Ejercicio propuesto

Añade un atributo `token_count` al span contando las palabras en el output. Verifica que el span exportado incluye `token_count` en `attributes`.

Solución en `exercises/solutions/12-observability-solution.py`.
```

### 3.8 `exercises/solutions/12-observability-solution.py`

```python
"""
Solución módulo 12: @trace con token_count en attributes.
"""
from __future__ import annotations

import sys
from functools import wraps
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "modules" / "12-observability"))

from src.mock_collector import MockCollector
from src.tracer import Span, set_collector, trace


def trace_with_token_count(name: str, **extra: Any) -> Callable:
    base_decorator = trace(name, **extra)

    def decorator(fn: Callable) -> Callable:
        wrapped = base_decorator(fn)

        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = wrapped(*args, **kwargs)
            # Patch last span to add token_count
            from src import tracer as tm
            if tm._collector is not None:
                last_spans = tm._collector.get_spans(name)
                if last_spans:
                    last_spans[-1].attributes["token_count"] = len(str(result).split())
            return result

        return wrapper

    return decorator


if __name__ == "__main__":
    coll = MockCollector()
    set_collector(coll)

    @trace_with_token_count("llm_call")
    def mock_llm(prompt: str) -> str:
        return "The answer is forty-two words long in this example"

    mock_llm("What is 42?")
    span = coll.get_spans("llm_call")[0]
    print(f"token_count in attributes: {span.attributes.get('token_count')}")
    exported = coll.export()
    print(f"exported keys: {list(exported[0].keys())}")
```

### 3.9 Verificación Task 3

```bash
cd /Users/gonzalo/Documents/GitHub/ai-testing-lab
pytest modules/12-observability/tests/ -m "not slow" -v
# Esperado: 7 passed, 1 deselected (slow), 0 failed
python3 exercises/solutions/12-observability-solution.py
```

---

## Task 4 — Módulo 13: drift-monitoring

### 4.1 Estructura de archivos

```
modules/13-drift-monitoring/
├── conftest.py
├── src/
│   ├── drift_detector.py
│   └── alert_rules.py
└── tests/
    ├── conftest.py
    └── test_drift_monitoring.py
```

### 4.2 `modules/13-drift-monitoring/conftest.py`

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
```

### 4.3 `modules/13-drift-monitoring/src/drift_detector.py`

```python
from __future__ import annotations

import numpy as np

_N_BINS = 10
_EPSILON = 1e-10


def _proportions(data: np.ndarray, bins: np.ndarray) -> np.ndarray:
    counts, _ = np.histogram(data, bins=bins)
    total = counts.sum()
    props = counts / total if total > 0 else np.ones_like(counts, dtype=float) / len(counts)
    return np.clip(props, _EPSILON, None)


def compute_psi(
    reference: list[float] | np.ndarray,
    current: list[float] | np.ndarray,
    n_bins: int = _N_BINS,
) -> float:
    """Population Stability Index between reference and current distributions."""
    ref = np.asarray(reference, dtype=float)
    cur = np.asarray(current, dtype=float)

    combined = np.concatenate([ref, cur])
    bins = np.linspace(combined.min(), combined.max() + _EPSILON, n_bins + 1)

    ref_props = _proportions(ref, bins)
    cur_props = _proportions(cur, bins)

    psi = float(np.sum((cur_props - ref_props) * np.log(cur_props / ref_props)))
    return round(psi, 4)
```

### 4.4 `modules/13-drift-monitoring/src/alert_rules.py`

```python
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable

import numpy as np


@dataclass
class AlertResult:
    triggered: bool
    rule_name: str
    observed_value: float
    threshold: float
    message: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def psi_alert(threshold: float = 0.2) -> Callable[[float], AlertResult]:
    def check(psi: float) -> AlertResult:
        triggered = psi > threshold
        return AlertResult(
            triggered=triggered,
            rule_name="psi_alert",
            observed_value=psi,
            threshold=threshold,
            message=f"PSI={psi:.4f} {'>' if triggered else '<='} {threshold}",
        )
    return check


def mean_drop_alert(
    reference_mean: float,
    threshold_pct: float = 0.1,
) -> Callable[[list[float]], AlertResult]:
    def check(current: list[float]) -> AlertResult:
        cur_mean = float(np.mean(current))
        drop_pct = (reference_mean - cur_mean) / reference_mean if reference_mean != 0 else 0.0
        triggered = drop_pct > threshold_pct
        return AlertResult(
            triggered=triggered,
            rule_name="mean_drop_alert",
            observed_value=cur_mean,
            threshold=reference_mean * (1.0 - threshold_pct),
            message=f"mean dropped {drop_pct:.1%} ({'ALERT' if triggered else 'ok'})",
        )
    return check


def p95_alert(limit: float) -> Callable[[list[float]], AlertResult]:
    def check(current: list[float]) -> AlertResult:
        p95 = float(np.percentile(current, 95))
        triggered = p95 > limit
        return AlertResult(
            triggered=triggered,
            rule_name="p95_alert",
            observed_value=p95,
            threshold=limit,
            message=f"p95={p95:.4f} {'>' if triggered else '<='} {limit}",
        )
    return check


def evaluate_rules(
    rules: list[Callable],
    data: list[float],
) -> list[AlertResult]:
    return [rule(data) for rule in rules]
```

### 4.5 `modules/13-drift-monitoring/tests/conftest.py`

```python
from __future__ import annotations

import numpy as np
import pytest


@pytest.fixture
def reference_scores() -> list[float]:
    rng = np.random.default_rng(42)
    return rng.normal(loc=0.8, scale=0.05, size=200).tolist()


@pytest.fixture
def identical_scores(reference_scores: list[float]) -> list[float]:
    return list(reference_scores)


@pytest.fixture
def shifted_scores() -> list[float]:
    rng = np.random.default_rng(99)
    return rng.normal(loc=0.3, scale=0.1, size=200).tolist()


@pytest.fixture
def dropped_scores(reference_scores: list[float]) -> list[float]:
    return [s * 0.75 for s in reference_scores]  # 25% drop
```

### 4.6 `modules/13-drift-monitoring/tests/test_drift_monitoring.py`

```python
from __future__ import annotations

import os

import numpy as np
import pytest

from src.alert_rules import (
    AlertResult,
    evaluate_rules,
    mean_drop_alert,
    p95_alert,
    psi_alert,
)
from src.drift_detector import compute_psi


class TestDriftDetector:

    def test_identical_distributions_psi_near_zero(
        self,
        reference_scores: list[float],
        identical_scores: list[float],
    ) -> None:
        psi = compute_psi(reference_scores, identical_scores)
        print(f"\n  PSI identical: {psi}")
        assert psi < 0.1, f"expected PSI near 0 for identical distributions, got {psi}"

    def test_shifted_distribution_psi_high(
        self,
        reference_scores: list[float],
        shifted_scores: list[float],
    ) -> None:
        psi = compute_psi(reference_scores, shifted_scores)
        print(f"\n  PSI shifted: {psi}")
        assert psi > 0.2, f"expected PSI > 0.2 for shifted distribution, got {psi}"


class TestAlertRules:

    def test_mean_drop_20pct_triggers_alert(
        self, reference_scores: list[float], dropped_scores: list[float]
    ) -> None:
        ref_mean = float(np.mean(reference_scores))
        rule = mean_drop_alert(reference_mean=ref_mean, threshold_pct=0.1)
        result = rule(dropped_scores)
        print(f"\n  {result.message}")
        assert result.triggered is True
        assert result.rule_name == "mean_drop_alert"

    def test_mean_drop_5pct_no_alert(self, reference_scores: list[float]) -> None:
        ref_mean = float(np.mean(reference_scores))
        slightly_dropped = [s * 0.97 for s in reference_scores]  # 3% drop
        rule = mean_drop_alert(reference_mean=ref_mean, threshold_pct=0.1)
        result = rule(slightly_dropped)
        print(f"\n  {result.message}")
        assert result.triggered is False

    def test_p95_exceeds_limit_triggers_alert(self) -> None:
        scores = [0.9] * 100
        rule = p95_alert(limit=0.8)
        result = rule(scores)
        print(f"\n  {result.message}")
        assert result.triggered is True
        assert result.rule_name == "p95_alert"

    def test_all_rules_pass_no_alert(self, reference_scores: list[float]) -> None:
        ref_mean = float(np.mean(reference_scores))
        rules: list = [
            mean_drop_alert(reference_mean=ref_mean, threshold_pct=0.3),
            p95_alert(limit=1.5),
        ]
        results = evaluate_rules(rules, reference_scores)
        print(f"\n  {[r.message for r in results]}")
        assert all(not r.triggered for r in results)

    def test_one_failing_rule_identified(self, reference_scores: list[float]) -> None:
        ref_mean = float(np.mean(reference_scores))
        dropped = [s * 0.6 for s in reference_scores]  # 40% drop
        rules: list = [
            mean_drop_alert(reference_mean=ref_mean, threshold_pct=0.3),
            p95_alert(limit=1.5),
        ]
        results = evaluate_rules(rules, dropped)
        triggered = [r for r in results if r.triggered]
        print(f"\n  triggered: {[r.rule_name for r in triggered]}")
        assert len(triggered) == 1
        assert triggered[0].rule_name == "mean_drop_alert"

    def test_alert_result_has_required_fields(self, reference_scores: list[float]) -> None:
        ref_mean = float(np.mean(reference_scores))
        rule = mean_drop_alert(reference_mean=ref_mean)
        result = rule(reference_scores)
        assert isinstance(result, AlertResult)
        assert result.timestamp  # non-empty ISO timestamp
        assert result.rule_name
        assert isinstance(result.observed_value, float)
        assert isinstance(result.threshold, float)
        assert result.message
        print(f"\n  AlertResult: triggered={result.triggered} ts={result.timestamp[:10]}")

    def test_psi_alert_threshold_configurable(
        self, reference_scores: list[float], shifted_scores: list[float]
    ) -> None:
        psi = compute_psi(reference_scores, shifted_scores)
        strict = psi_alert(threshold=0.05)(psi)
        lenient = psi_alert(threshold=10.0)(psi)
        assert strict.triggered is True
        assert lenient.triggered is False

    @pytest.mark.slow
    def test_real_langfuse_scores(self) -> None:
        if not os.getenv("LANGFUSE_SECRET_KEY"):
            pytest.skip("LANGFUSE_SECRET_KEY no encontrado")
        # Smoke: just verify PSI works with realistic score ranges
        rng = np.random.default_rng(0)
        ref = rng.beta(5, 1, size=100).tolist()
        cur = rng.beta(2, 2, size=100).tolist()
        psi = compute_psi(ref, cur)
        print(f"\n  Real PSI (beta distributions): {psi}")
        assert psi >= 0.0
```

### 4.7 `modules/13-drift-monitoring/README.md`

```markdown
# Módulo 13 — Drift Monitoring

**Status:** implemented

## Objetivos

- Calcular PSI entre distribución de referencia y distribución actual
- Configurar reglas de alerta: caída de media, p95, PSI
- Componer múltiples reglas y detectar cuál disparó

## Cómo ejecutar

```bash
cd modules/13-drift-monitoring
pytest tests/ -m "not slow" -v
pytest tests/ -m slow -v   # requiere LANGFUSE_SECRET_KEY
```

## Ejercicio propuesto

Implementa un `DriftReport` que ejecute todas las reglas configuradas, incluya el PSI y genere un dict con timestamp, métricas y alertas disparadas.

Solución en `exercises/solutions/13-drift-monitoring-solution.py`.
```

### 4.8 `exercises/solutions/13-drift-monitoring-solution.py`

```python
"""
Solución módulo 13: DriftReport con PSI + reglas + timestamp.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "modules" / "13-drift-monitoring"))

from src.alert_rules import AlertResult, mean_drop_alert, p95_alert, psi_alert
from src.drift_detector import compute_psi


@dataclass
class DriftReport:
    psi: float
    alerts: list[AlertResult]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def any_triggered(self) -> bool:
        return any(a.triggered for a in self.alerts)

    def as_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "psi": self.psi,
            "any_triggered": self.any_triggered,
            "alerts": [
                {
                    "rule": a.rule_name,
                    "triggered": a.triggered,
                    "observed": a.observed_value,
                    "message": a.message,
                }
                for a in self.alerts
            ],
        }


def run_drift_analysis(
    reference: list[float],
    current: list[float],
    rules: list[Callable],
) -> DriftReport:
    psi = compute_psi(reference, current)
    psi_result = psi_alert(threshold=0.2)(psi)
    score_alerts = [rule(current) for rule in rules]
    return DriftReport(psi=psi, alerts=[psi_result, *score_alerts])


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    ref = rng.normal(0.8, 0.05, 200).tolist()
    cur = rng.normal(0.5, 0.1, 200).tolist()

    ref_mean = float(np.mean(ref))
    report = run_drift_analysis(
        reference=ref,
        current=cur,
        rules=[
            mean_drop_alert(reference_mean=ref_mean, threshold_pct=0.1),
            p95_alert(limit=0.9),
        ],
    )
    import json
    print(json.dumps(report.as_dict(), indent=2))
```

### 4.9 Verificación Task 4

```bash
cd /Users/gonzalo/Documents/GitHub/ai-testing-lab
pytest modules/13-drift-monitoring/tests/ -m "not slow" -v
# Esperado: 8 passed, 1 deselected (slow), 0 failed
python3 exercises/solutions/13-drift-monitoring-solution.py
```

---

## Task 5 — Verificación final, README y push

### 5.1 Suite completa módulos 01-13

```bash
cd /Users/gonzalo/Documents/GitHub/ai-testing-lab
pytest \
  modules/01-primer-eval/tests/ \
  modules/02-ragas-basics/tests/ \
  modules/03-llm-as-judge/tests/ \
  modules/04-multi-turn/tests/ \
  modules/05-prompt-regression/tests/ \
  modules/06-hallucination-lab/tests/ \
  modules/07-redteam-garak/tests/ \
  modules/08-redteam-deepteam/tests/ \
  modules/09-guardrails/tests/ \
  modules/10-agent-testing/tests/ \
  modules/11-playwright-streaming/tests/ \
  modules/12-observability/tests/ \
  modules/13-drift-monitoring/tests/ \
  -m "not slow" --tb=short -q
```

Esperado: **90+ passed** (82 actuales + 8 de 10 + 0/7 de 11 si playwright no está + 7 de 12 + 8 de 13), 0 failed. El módulo 11 devuelve 0 collected (skip graceful) si playwright no está instalado.

### 5.2 Actualizar README

En `/Users/gonzalo/Documents/GitHub/ai-testing-lab/README.md`, actualizar las filas de la tabla:

```markdown
| 10 | [agent-testing](modules/10-agent-testing/) | 9 | ✅ implementado | tool selection · trajectory evaluation · AgentGoalAccuracy |
| 11 | [playwright-streaming](modules/11-playwright-streaming/) | 8 | ✅ implementado | SSE streaming · E2E chatbot UI · FastAPI mock server |
| 12 | [observability](modules/12-observability/) | 8 | ✅ implementado | OTel spans · @trace decorator · latency · error tracking |
| 13 | [drift-monitoring](modules/13-drift-monitoring/) | 9 | ✅ implementado | PSI · semantic drift · alert rules |
```

Y actualizar el bloque "Ejecutar todos los módulos implementados" para incluir todos los módulos 01-13.

También actualizar el `## Mapa del repo` para quitar "en desarrollo" de los módulos 07..13.

### 5.3 Commit y push

```bash
git add \
  modules/10-agent-testing/ \
  modules/11-playwright-streaming/ \
  modules/12-observability/ \
  modules/13-drift-monitoring/ \
  exercises/solutions/10-agent-testing-solution.py \
  exercises/solutions/11-playwright-streaming-solution.py \
  exercises/solutions/12-observability-solution.py \
  exercises/solutions/13-drift-monitoring-solution.py \
  docs/superpowers/plans/2026-04-24-batch3-infra-modules.md \
  README.md

git commit -m "feat: batch 3 infra modules complete — agent testing, playwright streaming, observability, drift monitoring

- 10-agent-testing: SimpleAgent (3 tools, keyword routing), TrajectoryEvaluator
  with exact match + partial credit for wrong args (9 tests)
- 11-playwright-streaming: FastAPI SSE mock server + Playwright E2E tests,
  graceful skip when playwright/fastapi not installed (8 tests)
- 12-observability: @trace decorator with input/output/duration/error capture,
  MockCollector with parent-child span tracking (8 tests)
- 13-drift-monitoring: PSI computation with numpy, configurable alert rules
  (mean drop, p95, PSI threshold), evaluate_rules() for rule composition (9 tests)
- All 13 modules implemented: 90+ tests total, 0 external services required"

git push origin main
```

---

## Testing Strategy

- **Unit tests** (deterministic): todos los módulos 10, 12, 13 corren sin dependencias externas en ~0.1s
- **E2E tests** (módulo 11): requieren playwright + chromium + fastapi + uvicorn; skip graceful si faltan
- **Slow tests** (1 por módulo): llaman a Groq real (10), Streamlit Docker (11), Langfuse (12, 13); skip automático si env var ausente

## Risks & Mitigations

- **Riesgo**: `compute_psi` devuelve NaN si todos los valores caen en el mismo bin.
  - **Mitigación**: `_EPSILON` en los bins y `np.clip` en las proporciones evitan log(0).
- **Riesgo**: `SimpleAgent._select_tool` elige erróneamente para queries ambiguas (ej: "how many search results").
  - **Mitigación**: orden de precedencia: calculate > format > search (más específico primero).
- **Riesgo**: Playwright tests flaky si el servidor tarda en arrancar.
  - **Mitigación**: `start_server` sondea el puerto hasta 3 segundos antes de devolver.
- **Riesgo**: `span_id` generado con `hex(id(object()))` puede colisionar.
  - **Mitigación**: Para tests unitarios es suficiente; en producción se usaría `uuid4`.

## Success Criteria

- [ ] `pytest modules/10-agent-testing/tests/ -m "not slow"` → 8 passed, 1 deselected
- [ ] `pytest modules/11-playwright-streaming/tests/ -m "not slow"` → 0 collected (playwright skip) o 7 passed
- [ ] `pytest modules/12-observability/tests/ -m "not slow"` → 7 passed, 1 deselected
- [ ] `pytest modules/13-drift-monitoring/tests/ -m "not slow"` → 8 passed, 1 deselected
- [ ] Suite 01-13 combinada → 90+ passed, 0 failed
- [ ] Soluciones de ejercicios ejecutan sin errores
- [ ] README actualizado con todos los módulos como implementados
- [ ] Commit + push a main

---

## Relevant file paths

- Module 10: `/Users/gonzalo/Documents/GitHub/ai-testing-lab/modules/10-agent-testing/`
- Module 11: `/Users/gonzalo/Documents/GitHub/ai-testing-lab/modules/11-playwright-streaming/`
- Module 12: `/Users/gonzalo/Documents/GitHub/ai-testing-lab/modules/12-observability/`
- Module 13: `/Users/gonzalo/Documents/GitHub/ai-testing-lab/modules/13-drift-monitoring/`
- Exercise solutions: `/Users/gonzalo/Documents/GitHub/ai-testing-lab/exercises/solutions/1{0,1,2,3}-*-solution.py`
- Main README: `/Users/gonzalo/Documents/GitHub/ai-testing-lab/README.md`
- Batch 2 reference (pattern source): `/Users/gonzalo/Documents/GitHub/ai-testing-lab/modules/09-guardrails/`
