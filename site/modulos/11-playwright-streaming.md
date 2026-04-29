---
title: "11 — playwright-streaming"
---

# 11 — playwright-streaming

Tests E2E de interfaces de chatbot con streaming SSE usando Playwright.

<div class="module-layout">
<div class="module-main">

## Qué aprenderás

- Cómo testear Server-Sent Events (SSE) con Playwright
- Montar un servidor mock de FastAPI para simular un chatbot en streaming
- Verificar que los tokens llegan en orden y sin corrupción
- Tests de regresión visual para UIs de chat

## Requisitos adicionales

```bash
pip install playwright pytest-playwright fastapi uvicorn
playwright install chromium
```

## Código de ejemplo

```python
async def test_streaming_completa_sin_errores(page):
    await page.goto("http://localhost:8765")
    await page.fill("#input", "¿Cuánto tarda el envío?")
    await page.click("#send")

    await page.wait_for_selector(".message.complete")
    content = await page.text_content(".message.assistant")
    assert len(content) > 10
    assert "error" not in content.lower()
```

## Por qué importa

> El streaming SSE tiene comportamientos que los tests de API no detectan: tokens fuera de orden, cortes en mitad de una palabra, o buffers que no se vacían correctamente.

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
