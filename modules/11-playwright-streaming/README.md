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
