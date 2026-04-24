# Módulo 11 — Playwright Streaming

**Status:** planned

## Objetivos

- Escribir tests E2E con Playwright para chatbots con respuestas en streaming (SSE)
- Hacer assertions sobre fragmentos de texto parciales y el estado del stream
- Integrar LLM-as-judge dentro de un test E2E para evaluar calidad de respuesta en UI

## Capítulo del manual

Este módulo cubre los conceptos de la sección X del manual (`docs/09-playwright-ui.md`).

## Conceptos clave

- Playwright para testing de UIs de chatbot con streaming SSE
- Assertions sobre streaming: verificar que el texto aparece progresivamente
- LLM-as-judge integrado en E2E: evaluar calidad sin código de evaluación separado
- Técnicas para lidiar con shadow DOM e iframes en chatbots embebidos

## Cómo ejecutar (pendiente)

```bash
# Disponible cuando el módulo esté implementado
cd modules/11-playwright-streaming
uv sync --extra ui
playwright install chromium
pytest tests/
```

## Ejercicio propuesto (pendiente)

_Descripción del ejercicio que se añadirá cuando se implemente el módulo._

## Estructura

```
11-playwright-streaming/
├── README.md
├── src/          # código del lab (pendiente)
└── tests/        # tests del lab (pendiente)
```
