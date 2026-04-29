# 11 — playwright-streaming

**Concepto:** Tests E2E de interfaces de chatbot con streaming SSE.

**Tests:** 8 · **Tiempo:** depende de Playwright · **API key:** no necesaria

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

## Ejecutar

```bash
pytest modules/11-playwright-streaming/tests/ -q
```

## Código de ejemplo

```python
async def test_streaming_completa_sin_errores(page):
    await page.goto("http://localhost:8765")
    await page.fill("#input", "¿Cuánto tarda el envío?")
    await page.click("#send")

    # Esperar a que el streaming termine
    await page.wait_for_selector(".message.complete")
    content = await page.text_content(".message.assistant")
    assert len(content) > 10
    assert "error" not in content.lower()
```

## Por qué importa

El streaming SSE tiene comportamientos específicos que los tests de API no detectan: tokens fuera de orden, cortes en mitad de una palabra, o buffers que no se vacían correctamente.
