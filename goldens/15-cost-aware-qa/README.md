# Golden dataset — 15-cost-aware-qa

100 observaciones estratificadas de queries en producción para el módulo 15.

## Estratificación

- **5 modelos** × **5 perfiles de query** × **4 variaciones** = 100 entradas.
- Modelos: `gpt-4o`, `gpt-4o-mini`, `claude-sonnet-4-5`, `claude-haiku-4-5`, `groq/llama-3.3-70b`.
- Perfiles: `simple_factual`, `rag_qa`, `agent_tool_use`, `creative_writing`, `structured_extraction`.
- Dominios mezclados: support, search, agent, summary.
- Risk tier (Tabla 4.2): low, medium, high.

## Esquema

```json
{
  "model": "gpt-4o-mini",
  "model_tier": "small",
  "query_profile": "simple_factual",
  "tokens_in": 80,
  "tokens_out": 40,
  "latency_ms_total": 547.3,
  "time_to_first_token_ms": 273.6,
  "tool_calls": 0,
  "retried": false,
  "cost_usd": 0.00003,
  "metadata": {
    "domain": "support",
    "risk_tier": "low",
    "language": "en",
    "golden_version": "1.0"
  }
}
```

## Regeneración

```bash
python scripts/generate_goldens_15_16.py
```

El script usa `random.Random(42)` para reproducibilidad. Los valores son
sintéticos pero realistas (precios fecha 2026-04, latencias coherentes con
benchmarks públicos).

## Política del manual (§9.2 y §9.4)

- Tamaño: 100 entradas ⇒ apto para regression mínimo. Para gate de release
  conservador, ampliar a 500–1000 con muestras reales de producción.
- Ratio sintético/real: este dataset es 100 % sintético (fase inicial). Antes
  de producción, el ratio debe pasar a 70 % real / 30 % sintético (§9.4).
- IAA: no aplica (el groundtruth de coste es objetivo: precio × tokens).
