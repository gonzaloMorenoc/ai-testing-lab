---
title: "12 — observability"
---

# 12 — observability

Instrumentar un pipeline LLM con OpenTelemetry. Trazas, latencia y error tracking.

<div class="module-layout">
<div class="module-main">

## Qué aprenderás

- Cómo crear spans OTel para cada etapa del pipeline (retrieval, generation, reranking)
- El decorador `@trace` para instrumentar funciones automáticamente
- Cómo conectar a Langfuse y Phoenix para visualizar trazas
- Métricas de latencia: dónde se pierde tiempo en el pipeline

## Código de ejemplo

```python
from src.tracer import trace, get_collector

@trace("retrieval")
def retrieve(query: str) -> list[str]:
    return buscar_en_vector_db(query)

@trace("generation")
def generate(query: str, context: list[str]) -> str:
    return llamar_llm(query, context)

with get_collector() as collector:
    respuesta = generate("¿Cuál es la política?", retrieve("política"))
    assert collector.span_count == 2
    assert collector.total_latency < 5.0
```

## Nuevas implementaciones (Manual QA AI v12)

**`TraceRecord`** — los 15 campos mandatorios de Tabla 16.1 (Cap 16 — Observabilidad):

```python
from src.trace_record import make_trace_record, validate_trace, TraceRecord

record = make_trace_record(
    response="Puedes devolver en 30 días.",
    tokens_in=120,
    tokens_out=18,
    latency_ms=342.5,
    model_id="claude-sonnet-4-6",
    prompt_id="return-policy-v2",
    prompt_version="2.1",
    retriever_id="faiss-cosine",
    top_k_docs=5,
    eval_scores={"faithfulness": 0.87, "relevancy": 0.91},
    safety_flags=(),
    pii_flags=(),
)

errors = validate_trace(record)
# errors = [] si todos los campos cumplen los requisitos mínimos
```

| Grupo | Campos |
|-------|--------|
| Identidad | `request_id`, `user_segment` |
| Modelo | `model_id`, `model_version` |
| Prompt | `prompt_id`, `prompt_version` |
| Retriever | `retriever_id`, `retriever_version`, `top_k_docs`, `reranker_scores` |
| Respuesta | `response`, `tokens_in`, `tokens_out`, `latency_ms` |
| Seguridad | `safety_flags`, `pii_flags`, `tool_calls` |
| Error | `error_code`, `retry_count` |
| Eval | `eval_scores` |

## Por qué importa

> Sin observabilidad, cuando el sistema es lento no sabes si el problema está en el retriever, en el reranker o en la llamada al LLM.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">8</div>
  <div class="stat-label">tests</div>
</div>

<div class="stat-card">
  <div class="stat-number">0.05s</div>
  <div class="stat-label">duración</div>
</div>

<div class="stat-card">
  <div class="stat-number">opt.</div>
  <div class="stat-label">API key</div>
</div>

<div class="stat-card">
  <div class="stat-number level">Avanzado</div>
  <div class="stat-label">nivel</div>
</div>

```bash
pytest modules/12-observability/tests/ \
  -m "not slow" -q
```

<div class="module-next">
  <div class="next-label">Siguiente →</div>
  <a href="/modulos/13-drift-monitoring">13 — drift-monitoring</a>
</div>

</div>
</div>
