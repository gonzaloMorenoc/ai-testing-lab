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
