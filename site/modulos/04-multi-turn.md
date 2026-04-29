---
title: "04 — multi-turn"
---

# 04 — multi-turn

Testear conversaciones de múltiples turnos y retención de información entre turnos.

<div class="module-layout">
<div class="module-main">

## Qué aprenderás

- `ConversationalTestCase` y cómo estructurar tests de diálogo
- Por qué el tamaño de la ventana de contexto importa (configurado en 8 turnos)
- Cómo verificar que la información del turno 1 sigue disponible en el turno 9
- Detección de contradicciones entre turnos

## Código de ejemplo

```python
from src.multi_turn_rag import MultiTurnRAG

rag = MultiTurnRAG()
rag.respond("¿Cuál es la política de devoluciones?")  # turno 1

# 7 turnos sobre otro tema...
for _ in range(7):
    rag.respond("¿Cuánto tarda el envío?")

# El turno 9 debe recordar el turno 1
response = rag.respond("¿Qué me dijiste sobre las devoluciones?")
assert "30 días" in response or "devolución" in response.lower()
```

## Por qué importa

> Un sistema RAG con ventana de contexto pequeña "olvida" información relevante a medida que avanza la conversación. El usuario siente que el sistema no le presta atención.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">14</div>
  <div class="stat-label">tests</div>
</div>

<div class="stat-card">
  <div class="stat-number">0.05s</div>
  <div class="stat-label">duración</div>
</div>

<div class="stat-card stat-ok">
  <div class="stat-number">✓</div>
  <div class="stat-label">sin API key</div>
</div>

<div class="stat-card">
  <div class="stat-number level">Intermedio</div>
  <div class="stat-label">nivel</div>
</div>

```bash
pytest modules/04-multi-turn/tests/ \
  -m "not slow" -q
```

<div class="module-next">
  <div class="next-label">Siguiente →</div>
  <a href="/modulos/05-prompt-regression">05 — prompt-regression</a>
</div>

</div>
</div>
