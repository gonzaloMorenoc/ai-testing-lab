# 12 — observability

**Concepto:** Instrumentar un pipeline LLM con OpenTelemetry. Trazas, latencia y error tracking.

**Tests:** 8 · **Tiempo:** ~0.05s · **API key:** no necesaria

## Qué aprenderás

- Cómo crear spans OTel para cada etapa del pipeline (retrieval, generation, reranking)
- El decorador `@trace` para instrumentar funciones automáticamente
- Cómo conectar a Langfuse y Phoenix para visualizar trazas
- Métricas de latencia: dónde se pierde tiempo en el pipeline

## Ejecutar

```bash
pytest modules/12-observability/tests/ -m "not slow" -q
```

## Código de ejemplo

```python
from src.tracer import trace, get_collector

@trace("retrieval")
def retrieve(query: str) -> list[str]:
    # El span se crea y cierra automáticamente
    return buscar_en_vector_db(query)

@trace("generation")
def generate(query: str, context: list[str]) -> str:
    return llamar_llm(query, context)

# En el test, verificar las trazas
with get_collector() as collector:
    respuesta = generate("¿Cuál es la política?", retrieve("política"))
    assert collector.span_count == 2
    assert collector.total_latency < 5.0
```

## Por qué importa

Sin observabilidad, cuando el sistema es lento no sabes si el problema está en el retriever, en el reranker o en la llamada al LLM. Las trazas OTel te dan visibilidad a nivel de función.
