# 15 — cost-aware-qa

Capítulo 27 del Manual QA AI v13: **el coste por inferencia es una métrica de QA de primer orden**, con sus propios gates y umbrales.

## Quickstart

```bash
pytest modules/15-cost-aware-qa/tests/ -m "not slow" -q
```

```
67 passed in 0.09s
```

## Qué cubre

- `CostReport` inmutable con `cost_usd` calculado por modelo desde `PRICE_PER_1K` externalizado.
- `assert_cost_budget` usando `raise BudgetExceededError` (no `assert`) para sobrevivir a `python -O` (§28.4).
- 7 métricas canónicas de la Tabla 27.1: tokens in/out, USD/query, latencia P50/P95/P99, TTFT, tool fan-out, retry rate.
- `CostRegressionChecker` con los umbrales Δ% por tipo de cambio (Tabla 27.2): prompt más largo (+15 %), modelo más caro (+20 %), top-k mayor (+25 %), agente con más loops (+30 %).
- 5 helpers de optimización (§27.5): cache hit rate, model routing, context compression, streaming UX, batching.
- Integración con la Tabla 4.2 raíz (`qa_thresholds.py`) para validar P95 latencia y Δ% coste.

## API pública

| Módulo | Símbolos |
|---|---|
| `src.price_config` | `PRICE_PER_1K`, `TokenPrice`, `load_prices_from_config` |
| `src.cost_report` | `CostReport`, `BudgetExceededError`, `UnknownModelError`, `assert_cost_budget` |
| `src.cost_metrics` | `QueryRecord`, `CostLatencyReport`, `compute_cost_latency_metrics` |
| `src.cost_regression` | `ChangeType`, `DELTA_THRESHOLDS`, `CostRegressionChecker`, `RegressionResult` |
| `src.optimizations` | `prompt_cache_hit_rate`, `simulate_model_routing`, `context_compression_ratio`, `streaming_perceived_latency`, `batching_efficiency` |

## Estructura

```
modules/15-cost-aware-qa/
├── conftest.py                 # inserta src/ y raíz del repo en sys.path
├── src/
│   ├── price_config.py
│   ├── cost_report.py
│   ├── cost_metrics.py
│   ├── cost_regression.py
│   └── optimizations.py
└── tests/
    ├── conftest.py             # fixtures compartidas (baseline_records)
    ├── test_price_config.py
    ├── test_cost_report.py
    ├── test_cost_metrics.py
    ├── test_cost_regression.py
    ├── test_optimizations.py
    └── test_integration_with_thresholds.py
```

## Diferencias con otros módulos

A diferencia de los módulos 01–14, este NO mide calidad funcional del LLM (faithfulness, refusal rate, etc.). Mide el **coste y la latencia** que cualquier cambio en el sistema produce: añadir un retrieval avanzado puede mejorar faithfulness pero triplicar tokens_in. Sin un gate de coste, esa regresión pasa silenciosa.

## Referencias del manual

- Cap. 27 — Cost-aware QA y observabilidad de costes (pp. 77–78)
- Tabla 4.2 — `qa_thresholds.py` raíz, gates de P95 latencia y Δ% coste
- §28.4 — Por qué `raise` y no `assert` en validaciones de runtime
