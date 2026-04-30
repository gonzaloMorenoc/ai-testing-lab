---
title: "12 — observability"
---

# 12 — observability

Instrumentar un pipeline LLM con OpenTelemetry. Trazas, latencia y error tracking.

<div class="module-layout">
<div class="module-main">

## El problema

Tu pipeline LLM tiene 3 segundos de latencia. ¿El problema está en el retriever, en el reranker o en la llamada al LLM? Sin trazas, la única forma de saberlo es añadir prints y volver a ejecutar. Con OpenTelemetry, cada etapa genera un span con su duración exacta. En producción, un pipeline sin observabilidad es una caja negra — solo sabes que algo falla, no dónde.

## Cómo funciona

- **Span OTel:** unidad de trazabilidad. Registra inicio, fin, duración y metadatos de una operación.
- **`@trace`:** decorador que envuelve una función y crea automáticamente un span con su nombre y duración.
- **`MockCollector`:** acumula los spans durante una ejecución y permite verificarlos en tests.
- **Langfuse y Phoenix:** plataformas de visualización de trazas LLM. El lab genera trazas compatibles con ambas.

```text
@trace("retrieval") → span_start → función → span_end
@trace("generation") → span_start → función → span_end
MockCollector → [span_retrieval, span_generation] → verificar count y latencia
```

## Código paso a paso

**1. Decorar funciones con `@trace`**

El decorador intercepta la llamada, mide el tiempo de ejecución y registra el span en el `MockCollector` activo. No requiere cambios en la lógica de la función.

```python
from src.tracer import trace
from src.mock_collector import MockCollector
import src.tracer as tracer_module

@trace("retrieval")
def retrieve(query: str) -> list[str]:
    return buscar_en_vector_db(query)

@trace("generation")
def generate(query: str, context: list[str]) -> str:
    return llamar_llm(query, context)
```

**2. Verificar `span_count` y latencia total**

`MockCollector` acumula todos los spans durante la ejecución. En los tests se usa como fixture para activarlo antes de la llamada y desactivarlo al terminar.

```python
collector = MockCollector()
tracer_module.set_collector(collector)

respuesta = generate("¿Cuál es la política?", retrieve("política"))

spans = collector.get_spans()
assert len(spans) == 2
total_latency = sum(s.duration_ms for s in spans)
assert total_latency < 5000  # ms
```

**3. Inspeccionar spans individuales por nombre**

`get_spans(name)` filtra por nombre de span. Permite verificar cada etapa del pipeline de forma independiente.

```python
retrieval_spans = collector.get_spans("retrieval")
generation_spans = collector.get_spans("generation")

assert len(retrieval_spans) == 1
assert retrieval_spans[0].status == "OK"
assert retrieval_spans[0].duration_ms >= 0
```

## Técnicas avanzadas

En producción, necesitas que cada traza sea completa y estructurada para que el equipo de oncall pueda diagnosticar incidencias sin necesitar al desarrollador que escribió el código. El módulo incluye `TraceRecord` con sus 20 campos, y `make_trace_record` y `validate_trace` para construir y validar registros de traza.

```python
from src.trace_record import make_trace_record, validate_trace

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

## Errores comunes

- **Spans sin correlación entre sí.** No puedes reconstruir el pipeline completo. Usar el mismo `trace_id` para todos los spans de una request.
- **Medir solo latencia total.** No sabes el cuello de botella. Un span por etapa: retrieval, reranking, generation.
- **Logs no estructurados (`print`).** No son consultables en Langfuse o Phoenix. Usar structured logging con los campos de `TraceRecord`.
- **No registrar tokens_in/out.** No puedes calcular el coste por request. Registrar siempre ambos contadores.

## En producción

| Campo | Por qué importa |
|-------|----------------|
| `trace_id` | Correlacionar spans de una request |
| `model_id` | Detectar regresiones por versión |
| `latency_ms` | SLA y alertas de rendimiento |
| `tokens_in` / `tokens_out` | Control de costes |
| `error_type` | Clasificar incidencias |

```bash
pytest modules/12-observability/tests/ -m "not slow" -q
```

Para detectar degradación de latencia en el tiempo, ver módulo 13.

## Caso real en producción

Una plataforma de sanidad con asistente de triaje reportaba un p95 de 4.2 segundos sin saber la causa. Tras instrumentar con `@trace` las tres etapas del pipeline, descubrieron que el reranker tardaba 2.8 segundos — el 67% de la latencia total. El retriever y el generador eran rápidos. La solución fue cachear los resultados del reranker para queries frecuentes, reduciendo el p95 a 1.6 segundos.

## Ejercicios

- 🟢 Añade un cuarto span al pipeline del lab (`@trace("postprocessing")`). Busca el archivo de test en `modules/12-observability/tests/test_observability.py` y ejecuta `pytest modules/12-observability/tests/ -m "not slow" -q`. ¿Sube el número de spans en el collector?
- 🟡 Implementa un test que verifique que si una etapa tarda más de 2 segundos, el span tiene `duration_ms > 2000`. Usa un mock con sleep controlado.
- 🔴 Genera 10 `TraceRecord` simulando latencia real con varianza. Pásalos por `validate_trace` y construye un informe con p50, p95 y p99 de latencia por etapa.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">22</div>
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
