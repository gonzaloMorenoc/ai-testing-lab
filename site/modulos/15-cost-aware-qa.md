---
title: "15 — cost-aware-qa"
---

# 15 — cost-aware-qa

El coste por inferencia es una métrica de QA de primer orden. Este módulo añade `CostReport`, métricas de latencia P50/P95/P99 y gates de regresión Δ% por tipo de cambio.

## El problema

Un PR puede no degradar `faithfulness` y aun así triplicar el coste por query. Cambiar de Haiku a Sonnet sube la calidad un 2 % y multiplica el coste por 10. Activar un retriever avanzado mejora `recall` pero añade 200 ms y un LLM call extra. Sin un gate de coste en CI, todas estas regresiones pasan silenciosas hasta que llega la factura mensual.

El **Capítulo 27 del manual v13** sube el coste a métrica de primer orden, con sus propios umbrales (Tabla 27.1) y sus propios gates de regresión por tipo de cambio (Tabla 27.2).

## Cómo funciona

### `CostReport`: contrato inmutable

`CostReport(model, tokens_in, tokens_out)` calcula `cost_usd` con `PRICE_PER_1K`, un diccionario externalizado a configuración. Nunca se hardcodean precios en código de runtime; los proveedores los cambian con frecuencia y un literal `0.0025` en un módulo es un detonador silencioso.

```python
from src.cost_report import CostReport, assert_cost_budget

report = CostReport(model="gpt-4o-mini", tokens_in=1200, tokens_out=400)
print(f"{report.cost_usd:.4f} USD")  # 0.0004

# raise BudgetExceededError si supera el presupuesto. Usa raise, no assert,
# para sobrevivir a python -O / PYTHONOPTIMIZE=1 (Manual §28.4).
assert_cost_budget(report, max_usd=0.001)
```

### 7 métricas de la Tabla 27.1

| Métrica | Umbral típico |
|---|---|
| Tokens entrada / query | definido por baseline |
| Tokens salida / query | ≤ 2× baseline |
| Coste USD / query | definido por presupuesto |
| Latencia P50 / P95 / P99 | P95 ≤ 2 s (chat) / ≤ 5 s (RAG) |
| Time-to-first-token | ≤ 1 s |
| Tool fan-out | ≤ 5 por defecto |
| Retry rate | ≤ 1 % |

```python
from src.cost_metrics import compute_cost_latency_metrics

report = compute_cost_latency_metrics(query_records)
assert report.latency_p95_ms <= 2000  # gate Tabla 4.2
assert report.retry_rate <= 0.01
```

### Regresión por tipo de cambio (Tabla 27.2)

```python
from src.cost_regression import CostRegressionChecker, ChangeType

checker = CostRegressionChecker()
result = checker.check(baseline, candidate, ChangeType.PROMPT_LONGER)
# Tolerable hasta +15 % en tokens_in_mean para un prompt más largo.
assert result.passed, result.violations
```

| Tipo de cambio | Métrica afectada | Δ tolerado |
|---|---|---|
| Prompt más largo | tokens_in_mean | +15 % |
| Modelo más caro | cost_usd_mean | +20 % |
| Top-k retrieval mayor | tokens_in_mean | +25 % |
| Agente con más loops | tool_fan_out, cost_usd | +30 % |

### Integración con la Tabla 4.2

El módulo importa los umbrales de `qa_thresholds.py` raíz. P95 latencia y Δ% coste están en la **Tabla maestra**, no duplicados aquí:

```python
from qa_thresholds import QA_THRESHOLDS, RiskLevel, evaluate_gates

# Usa los umbrales canónicos
results = evaluate_gates(
    {"p95_latency_seconds": 0.8, "cost_per_query_delta_pct": 7.5},
    level=RiskLevel.TARGET,
)
assert all(r.passed for r in results)
```

## Las 5 optimizaciones del §27.5

| Optimización | Helper | Cuándo aplicar |
|---|---|---|
| Prompt caching | `prompt_cache_hit_rate` | Anthropic / OpenAI nativo; system prompts grandes |
| Model routing | `simulate_model_routing` | Queries cortas → Haiku/Mini; complejas → Sonnet/4o |
| Context compression | `context_compression_ratio` | RAG con contextos > 4k tokens |
| Streaming | `streaming_perceived_latency` | UX de respuestas largas (no reduce coste, mejora P95 percibido) |
| Batching | `batching_efficiency` | Evaluaciones offline en batch reducen overhead |

## Anti-patrones cubiertos

- **AP de coste #1: `assert` en validaciones de presupuesto.** `assert` se desactiva con `python -O`. El módulo usa `raise BudgetExceededError`.
- **AP de coste #2: precios hardcoded.** El módulo carga `PRICE_PER_1K` desde una función que admite override por config externa.
- **AP de coste #3: solo medir media.** El módulo reporta P50/P95/P99 y tool_fan_out_mean, no solo cost_usd_mean.

## Referencias

- Manual QA AI v13 — Cap. 27 (pp. 77–78), Tablas 27.1 y 27.2
- Tabla 4.2 — [`qa_thresholds.py`](https://github.com/gonzaloMorenoc/ai-testing-lab/blob/main/qa_thresholds.py)
- §28.4 — Por qué `raise` y no `assert` en runtime
