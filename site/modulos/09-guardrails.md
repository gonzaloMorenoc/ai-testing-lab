# 09 — guardrails

**Concepto:** Validación de entrada y salida con Guardrails AI y NeMo Guardrails.

**Tests:** 11 · **Tiempo:** ~0.05s · **API key:** no necesaria

## Qué aprenderás

- Pipeline de validación I/O: qué validar antes de llamar al LLM y después
- Detección de PII (información personal identificable) en inputs y outputs
- Rails conversacionales con NeMo Guardrails (Colang DSL)
- Cuándo usar guardrails de reglas vs guardrails basados en LLM

## Ejecutar

```bash
pytest modules/09-guardrails/tests/ -m "not slow" -q
```

## Código de ejemplo

```python
from src.guardrail_pipeline import GuardrailPipeline

pipeline = GuardrailPipeline()
result = pipeline.run(
    user_input="Mi email es usuario@ejemplo.com. ¿Cuál es mi saldo?",
)

print(result.blocked)       # True — PII detectada en el input
print(result.reason)        # "pii_detected"
print(result.pii_found)     # ["usuario@ejemplo.com"]
```

## Por qué importa

Sin guardrails, los usuarios pueden enviar datos sensibles que el LLM procesa y potencialmente memoriza o incluye en respuestas a otros usuarios. También protege contra inyecciones de prompt en el input.
