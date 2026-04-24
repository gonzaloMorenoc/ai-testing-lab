# Módulo 09 — Guardrails de I/O

**Status:** implemented

## Objetivos

- Validar inputs antes de llegar al LLM (PII, toxicidad, longitud)
- Validar outputs antes de devolverlos al usuario (system prompt leak, PII blocklist, JSON schema)
- Componer ambos validadores en un pipeline que aborte antes de invocar al modelo si el input es inseguro

## Cómo ejecutar

```bash
cd modules/09-guardrails
pytest tests/ -m "not slow" -v
pytest tests/ -m slow -v   # requiere GROQ_API_KEY
```

## Ejercicio propuesto

Implementa un `CompositeGuardrail` que corra varios `OutputValidator` en secuencia y devuelva la primera violación encontrada, con métricas de cuántas reglas se evaluaron.

Solución en `exercises/solutions/09-guardrails-solution.py`.
