---
title: "04 — multi-turn"
---

# 04 — multi-turn

Testear conversaciones de múltiples turnos y retención de información entre turnos.

<div class="module-layout">
<div class="module-main">

## El problema

Un chatbot que responde bien en una sola interacción puede fallar en conversaciones largas. Si el usuario menciona su dirección en el turno 1 y hace una pregunta relacionada en el turno 7, el sistema necesita retener esa información. La mayoría de los tests de LLMs evalúan turnos individuales y no detectan cuándo el modelo olvida información crítica a medida que avanza la conversación.

## Cómo funciona

El evaluador de multi-turn opera sobre una `Conversation` estructurada y calcula 7 métricas deterministas — sin llamadas a ningún LLM:

- **`context_retention`**: fracción de hechos clave aún referenciados en turnos posteriores.
- **`coreference_resolution`**: fracción de pronombres resueltos correctamente en el turno siguiente.
- **`consistency`**: similitud BoW entre respuestas equivalentes en distintos turnos.
- **`topic_tracking`**: fracción de turnos con el topic correcto.
- **`memory_window_used`**: cuántos turnos atrás fue recordado el hecho más antiguo.
- **`context_overflow_detected`**: `True` si `num_turns > memory_window`.
- **`conversation_summarization_score`**: overlap entre el resumen y el contenido de la conversación.

```text
[turno 1] → [turno 2] → ... → [turno N]
                                   ↓
                          MultiTurnEvaluator
                                   ↓
  {context_retention, consistency, topic_tracking, ...}
```

## Código paso a paso

**Paso 1 — Construir la conversación con `add_turn`**

```python
from src.conversation import Conversation

conv = Conversation()
conv.add_turn(
    "¿Cuál es la política de devoluciones?",
    "Aceptamos devoluciones en 30 días con el ticket de compra.",
)
conv.add_turn(
    "¿Y los gastos de envío?",
    "Envío gratis a partir de 50€.",
)
conv.add_turn(
    "¿Qué pasa si el producto llega dañado?",
    "Gestionamos el cambio sin coste adicional.",
)
```

**Paso 2 — Definir `key_facts` y `pronoun_entity_pairs`**

```python
# Hechos que deben seguir presentes en turnos posteriores
key_facts = ["30 días", "50€"]

# Pronombres que el asistente debe resolver correctamente
pronoun_entity_pairs = [("it", "devolución"), ("eso", "política")]

expected_topics = ["devoluciones", "envío", "daños"]
summary = "El chatbot explicó la política de devoluciones, envío y productos dañados."
```

**Paso 3 — Ejecutar el evaluador e interpretar resultados**

```python
from src.multi_turn_metrics import MultiTurnEvaluator, MULTI_TURN_THRESHOLD

evaluator = MultiTurnEvaluator(memory_window=8, threshold=MULTI_TURN_THRESHOLD)
report = evaluator.evaluate(
    conv=conv,
    key_facts=key_facts,
    pronoun_entity_pairs=pronoun_entity_pairs,
    expected_topics=expected_topics,
    summary=summary,
)

print(report.context_retention)        # hechos clave retenidos
print(report.consistency)              # coherencia entre turnos
print(report.context_overflow_detected) # True si supera memory_window
print(report.passed)                    # True si todas las métricas >= threshold

if not report.passed:
    print("Revisa context_retention o consistency")
```

## Técnicas avanzadas

Cuando necesitas un diagnóstico completo de la salud conversacional más allá de verificar si el turno N recuerda el turno 1, estas 7 métricas te dan una visión detallada de cada dimensión. La tabla completa:

| Métrica | Descripción |
|---------|-------------|
| `context_retention` | % de hechos anteriores aún referenciados |
| `coreference_resolution` | % de pronombres resueltos correctamente |
| `consistency` | similitud BoW entre respuestas equivalentes |
| `topic_tracking` | % de turnos con topic correcto |
| `memory_window_used` | turnos atrás que fueron recordados |
| `context_overflow_detected` | True si num_turns > memory_window |
| `conversation_summarization_score` | overlap entre resumen y conversación |

Puedes instanciar el evaluador con todos los parámetros explícitos para tener control total:

```python
from src.multi_turn_metrics import MultiTurnEvaluator, MULTI_TURN_THRESHOLD

evaluator = MultiTurnEvaluator(
    memory_window=4,     # ventana más corta → detecta overflow antes
    threshold=0.80,      # umbral más estricto que el por defecto (0.70)
)

# Métricas individuales también disponibles directamente:
retention = evaluator.context_retention(conv, key_facts=["30 días"])
overflow = evaluator.context_overflow_detected(conv)
window_used = evaluator.memory_window_used(conv, fact="30 días")
```

## Errores comunes

- **Tests de un solo turno para validar un chatbot conversacional** — no detecta pérdida de contexto. Siempre incluye tests de ≥ 5 turnos.
- **No testear el límite de la `memory_window`** — el sistema puede funcionar en tests cortos y fallar en producción. Incluye un test con `num_turns > memory_window`.
- **No verificar coreferencialidad** — "¿cuánto cuesta?" no tiene sentido sin saber a qué se refiere "eso" del turno anterior. Define `pronoun_entity_pairs`.
- **Conversaciones de test demasiado cortas** — no ejercitan el sistema. Incluye tests de 8-12 turnos.

## En producción

| Métrica             | Umbral mínimo |
|---------------------|---------------|
| context_retention   | ≥ 0.80        |
| consistency         | ≥ 0.75        |
| topic_tracking      | ≥ 0.85        |

Ejecuta los tests en CI con:

```bash
pytest modules/04-multi-turn/tests/ -m "not slow" -q
```

## Caso real en producción

E-commerce con chatbot de seguimiento de pedidos. Los usuarios mencionaban la dirección de envío en el primer turno y preguntaban detalles del pedido durante los siguientes 5-6 turnos. Tras el turno 7, el chatbot dejaba de referenciar la dirección original. `context_overflow_detected` se activaba y `context_retention` caía a 0.45. La solución fue reducir la verbosidad de las respuestas para que más información cupiera en la ventana de contexto.

## Ejercicios

**🟢 Básico** — Construye una conversación de 10 turnos donde el dato clave se menciona en el turno 1. Configura `memory_window=8`. El archivo de test está en `modules/04-multi-turn/tests/test_multi_turn.py`. Ejecuta:

```bash
pytest modules/04-multi-turn/tests/ -m "not slow" -q
```

Verifica que `context_overflow_detected` es `True`.

**🟡 Intermedio** — Añade pronombres ambiguos a la conversación ("¿y eso?", "¿el de antes?") y mide cómo afecta a `coreference_resolution`. ¿Qué patrones en el texto provocan el mayor descenso?

**🔴 Avanzado** — Implementa un test de regresión que compare dos versiones de un sistema de chat: una con `memory_window=4` y otra con `memory_window=12`. Usa `MultiTurnEvaluator` para demostrar cuantitativamente cuál retiene mejor el contexto.

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
