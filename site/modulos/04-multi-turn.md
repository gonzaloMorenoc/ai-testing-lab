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

## Nuevas implementaciones (Manual QA AI v12)

**`MultiTurnEvaluator`** — las 7 métricas de conversación de Tabla 13.1 (Cap 13), todas deterministas sin LLM:

```python
from src.multi_turn_metrics import MultiTurnEvaluator, MULTI_TURN_THRESHOLD
from src.conversation import Conversation

conv = Conversation()
conv.add_turn("¿Cuál es la política de devoluciones?", "30 días para devoluciones completas.")
conv.add_turn("¿Y los gastos de envío?", "Envío gratis a partir de 50€.")

evaluator = MultiTurnEvaluator(memory_window=8, threshold=MULTI_TURN_THRESHOLD)
report = evaluator.evaluate(
    conv=conv,
    key_facts=["30 días", "50€"],
    pronoun_entity_pairs=[("it", "devolución")],
    expected_topics=["devoluciones", "envío"],
    summary="El chatbot habló de devoluciones y envío.",
)
# report.context_retention, report.consistency, report.passed
```

| Métrica | Descripción |
|---------|-------------|
| `context_retention` | % de hechos anteriores aún referenciados |
| `coreference_resolution` | % de pronombres resueltos correctamente |
| `consistency` | similitud BoW entre respuestas equivalentes |
| `topic_tracking` | % de turnos con topic correcto |
| `memory_window_used` | turnos atrás que fueron recordados |
| `context_overflow_detected` | True si num_turns > memory_window |
| `conversation_summarization_score` | overlap entre resumen y conversación |

## Por qué importa

> Un sistema RAG con ventana de contexto pequeña "olvida" información relevante a medida que avanza la conversación. El usuario siente que el sistema no le presta atención.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">29</div>
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
