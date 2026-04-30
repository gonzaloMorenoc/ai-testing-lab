---
title: "11 — playwright-streaming"
---

# 11 — playwright-streaming

Tests E2E de interfaces de chatbot con streaming SSE usando Playwright.

<div class="module-layout">
<div class="module-main">

## El problema

Los tests de API verifican que el endpoint devuelve el contenido correcto. Pero si la interfaz usa streaming, pueden ocurrir fallos invisibles para los tests de API: tokens fuera de orden, cortes en mitad de una palabra, buffers que no se vacían, o la UI que congela esperando el primer chunk. El único test que detecta estos fallos es uno que abre un navegador real y observa la interfaz mientras recibe los tokens.

## Cómo funciona

- **Server-Sent Events (SSE):** el servidor envía chunks de texto de forma continua. El cliente los recibe y renderiza progresivamente.
- **FastAPI + mock server:** el lab monta un servidor mock que simula el streaming sin llamadas a APIs externas.
- **Playwright** intercepta la interfaz y verifica que los tokens llegan en orden y sin corrupción.
- **`wait_for_selector`:** sincronización explícita — los tests deben esperar a que el streaming complete antes de verificar el contenido.

```text
pytest fixture → uvicorn mock (puerto 8765) → Playwright → navegador real → SSE chunks → UI → assert contenido completo
```

## Código paso a paso

**1. Fixture que arranca el servidor mock**

El conftest de sesión localiza un puerto libre, llama a `start_server` y devuelve la URL base. Todos los tests del módulo reciben `server_url` sin levantar el servidor más de una vez.

```python
# modules/11-playwright-streaming/tests/conftest.py
import socket
import pytest

def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("", 0))
        return s.getsockname()[1]

@pytest.fixture(scope="session")
def server_url() -> str:
    port = _free_port()
    from src.mock_chat_server import start_server
    start_server(port)
    return f"http://127.0.0.1:{port}"
```

**2. Navegar, enviar mensaje y esperar el streaming completo**

El atributo `data-complete="true"` se activa cuando el servidor envía `{"done": true}`. Esperar este atributo garantiza que el streaming ha terminado antes de hacer cualquier aserción.

```python
def test_response_complete_attribute(page: Page, server_url: str) -> None:
    page.goto(server_url)
    page.fill("#input", "complete test")
    page.click("#send")
    expect(page.locator("#response")).to_have_attribute(
        "data-complete", "true", timeout=10_000
    )
    text = page.locator("#response").text_content()
    assert text and len(text) > 0
```

**3. Verificar el contenido y la ausencia de errores**

Una vez que el streaming ha completado, se puede extraer el texto y validar su contenido con expresiones regulares.

```python
def test_regex_on_response(page: Page, server_url: str) -> None:
    page.goto(server_url)
    page.fill("#input", "hello")
    page.click("#send")
    expect(page.locator("#response")).to_have_attribute(
        "data-complete", "true", timeout=10_000
    )
    text = page.locator("#response").text_content() or ""
    assert re.search(r"Echo:", text, re.IGNORECASE), f"Unexpected response: {text!r}"
```

## Errores comunes

- **Asumir que si la API funciona la UI también.** SSE tiene comportamientos específicos de la capa de presentación. Siempre testear la UI con Playwright.
- **Tests sin espera explícita.** Sin `to_have_attribute("data-complete", "true")` o similar, existe una race condition entre el streaming y la verificación. El test puede pasar a veces y fallar otras.
- **No testear reconexión tras desconexión.** El cliente SSE puede no recuperarse automáticamente si la conexión se interrumpe a mitad del streaming.
- **Tests E2E en CI sin servidor levantado.** El test pasa localmente pero falla en CI porque no hay servidor. La fixture de pytest que levanta el servidor antes del test soluciona esto.

## En producción

```bash
# Arrancar servidor mock
uvicorn modules.11-playwright-streaming.src.mock_chat_server:app --port 8765 &

# Ejecutar tests E2E
pytest modules/11-playwright-streaming/tests/ -m "not slow" -q
```

Para observabilidad del pipeline de streaming, ver módulo 12.

## Caso real en producción

Una plataforma de generación de contenido para medios con editor IA pasaba todos los tests de API correctamente, pero el 4% de los usuarios reportaban que el texto se "cortaba" a mitad de frase. Los tests Playwright con interceptación SSE revelaron que el cliente no manejaba correctamente chunks que llegaban partidos en mitad de un carácter Unicode multibyte. El bug no era detectable sin un test E2E con navegador real.

## Ejercicios

- 🟢 Añade un test que verifique que si el servidor devuelve un error HTTP 500, la UI muestra un mensaje de error — no una pantalla en blanco. Verifica el archivo de test existente en `modules/11-playwright-streaming/tests/test_playwright_streaming.py` y ejecuta `pytest modules/11-playwright-streaming/tests/ -m "not slow" -q`.
- 🟡 Implementa un test que simule una desconexión SSE a mitad del streaming y verifica que el cliente intenta reconectar y el mensaje queda marcado como incompleto.
- 🔴 Añade tests de regresión visual con `page.screenshot()`: captura el estado de la UI antes del primer token, durante el streaming y después del mensaje completo. Verifica que los tres estados tienen el markup correcto.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">8+</div>
  <div class="stat-label">tests</div>
</div>

<div class="stat-card">
  <div class="stat-number">E2E</div>
  <div class="stat-label">duración</div>
</div>

<div class="stat-card">
  <div class="stat-number">⚙</div>
  <div class="stat-label">playwright</div>
</div>

<div class="stat-card">
  <div class="stat-number level">Avanzado</div>
  <div class="stat-label">nivel</div>
</div>

```bash
pip install playwright
playwright install chromium
pytest modules/11-playwright-streaming/tests/
```

<div class="module-next">
  <div class="next-label">Siguiente →</div>
  <a href="/modulos/12-observability">12 — observability</a>
</div>

</div>
</div>
