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
