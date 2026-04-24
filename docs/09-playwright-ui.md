# Playwright para UIs de chatbot

> Parte del [Manual de Testing de Chatbots y LLMs](./manual-completo.md).

---

## 11. Playwright para UIs de chatbot

### 11.1 Retos específicos
- Respuestas **streaming** (aparecen token a token).
- Contenido **no determinista** – no se puede aserción por texto exacto.
- Widgets **embebidos en iframes** con Shadow DOM.
- **Esperas**: sin timeouts fijos; usa auto-waiting de Playwright.

### 11.2 Patrón recomendado
```python
import re
from playwright.sync_api import Page, expect

def test_password_reset_intent(page: Page):
    page.goto("https://app.example.com/chat")
    page.get_by_role("textbox", name="Mensaje").fill("¿cómo reseteo mi clave?")
    page.get_by_role("button", name="Enviar").click()

    last_bot = page.locator('[data-testid="bot-message"]').last
    # Espera a que termine el streaming
    expect(last_bot).to_have_attribute("data-complete", "true", timeout=30_000)
    text = last_bot.inner_text()

    # Asserts no deterministas: regex + evaluador semántico
    assert re.search(r"(reset|restablec|recuperar)", text, re.IGNORECASE)

    # Delegar la validación semántica a DeepEval (LLM-as-judge)
    from deepeval.metrics import GEval
    from deepeval.test_case import LLMTestCase, LLMTestCaseParams
    metric = GEval(
        name="IntentoCorrecto",
        criteria="La respuesta debe guiar al usuario a resetear su contraseña y no pedir información sensible.",
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.INPUT],
        threshold=0.7,
    )
    metric.measure(LLMTestCase(input="¿cómo reseteo mi clave?", actual_output=text))
    assert metric.is_successful(), metric.reason
```

### 11.3 Streaming bien hecho
Tres estrategias ([medium.com/@gunashekarr11](https://medium.com/@gunashekarr11/testing-ai-chatbots-with-playwright-the-future-nobody-is-ready-for-64495def2c40), [opcito.com](https://www.opcito.com/blogs/using-playwright-for-genai-app-testing)):
1. **Data-attribute flag** (`data-complete="true"`) que la app expone cuando termina la respuesta.
2. **Wait for network idle** del endpoint SSE.
3. **Polling de estabilización**: el texto no cambia en X ms → considerado completo.

### 11.4 Widgets embebidos / iframes
```python
frame = page.frame_locator("iframe[title='Chatbot']")
frame.get_by_role("textbox").fill("...")
```

### 11.5 Asserts sobre contenido dinámico
Combina:
- **Regex / contains** para palabras obligatorias (PII redaction, mencionar marca).
- **Schema validation** si tu bot devuelve JSON estructurado.
- **LLM-as-judge** (delegate) para lo semántico.
- **Screenshot testing** para el layout (no para el texto).

### 11.6 Playwright 1.59 para agentes de QA
Features recientes útiles: `browser.bind()` para compartir browser entre CLI/MCP/tests, `npx playwright trace` CLI para debugging por agentes de código, `page.screencast()` con overlays anotados ([testdino.com](https://testdino.com/blog/playwright-release-guide/)). Ideal si integras Claude Code / Cursor para generar tests automáticamente.

### 11.7 Proyecto de referencia
Hay un repo `bot-test-playwright` con suites ya organizadas en RAGAS compliance, security (prompt injection), retrieval/performance, multi-turn y UX ([github.com/dkoul/bot-test-playwright](https://github.com/dkoul/bot-test-playwright)). Útil como plantilla.

---

## Laboratorios relacionados

| Módulo | Descripción |
|--------|-------------|
| [11-playwright-streaming](../modules/11-playwright-streaming/) | Playwright + streaming assertions + LLM-as-judge integrado |
| [demos/streamlit-chat](../demos/streamlit-chat/) | Target UI con SSE streaming para practicar |
