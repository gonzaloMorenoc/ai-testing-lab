---
title: "09 — guardrails"
---

# 09 — guardrails

Validación de entrada y salida con Guardrails AI y NeMo Guardrails.

<div class="module-layout">
<div class="module-main">

## Qué aprenderás

- Pipeline de validación I/O: qué validar antes de llamar al LLM y después
- Detección de PII (información personal identificable) en inputs y outputs
- Rails conversacionales con NeMo Guardrails (Colang DSL)
- Cuándo usar guardrails de reglas vs guardrails basados en LLM

## Código de ejemplo

```python
from src.guardrail_pipeline import GuardrailPipeline

pipeline = GuardrailPipeline()
result = pipeline.run(
    user_input="Mi email es usuario@ejemplo.com. ¿Cuál es mi saldo?",
)

print(result.blocked)    # True — PII detectada en el input
print(result.reason)     # "pii_detected"
print(result.pii_found)  # ["usuario@ejemplo.com"]
```

## Por qué importa

> Sin guardrails, los usuarios pueden enviar datos sensibles que el LLM procesa y potencialmente incluye en respuestas a otros usuarios.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">11</div>
  <div class="stat-label">tests</div>
</div>

<div class="stat-card">
  <div class="stat-number">0.06s</div>
  <div class="stat-label">duración</div>
</div>

<div class="stat-card stat-ok">
  <div class="stat-number">✓</div>
  <div class="stat-label">sin API key</div>
</div>

<div class="stat-card">
  <div class="stat-number level">Avanzado</div>
  <div class="stat-label">nivel</div>
</div>

```bash
pytest modules/09-guardrails/tests/ \
  -m "not slow" -q
```

<div class="module-next">
  <div class="next-label">Siguiente →</div>
  <a href="/modulos/10-agent-testing">10 — agent-testing</a>
</div>

</div>
</div>
