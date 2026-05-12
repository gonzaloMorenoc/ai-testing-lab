# 16 — retrieval-advanced

Capítulo 29 del Manual QA AI v13: técnicas de retrieval avanzado (HyDE, query rewriting, multi-query, hybrid search, reranking, parent-child, sentence-window, Self-RAG) y cómo testear si **justifican su coste extra**.

## Quickstart

```bash
pytest modules/16-retrieval-advanced/tests/ -m "not slow" -q
```

```
66 passed in 0.09s
```

## Qué cubre

- 8 técnicas de retrieval avanzado, cada una con mock determinista (sin LLM real).
- Métricas IR: NDCG@k, MRR@k, MAP@k (implementación interna, sin dependencia obligatoria de `ranx`).
- `ComparisonReport.justified`: gate canónico del manual §29.3 — una técnica solo se justifica si Δ NDCG@5 ≥ +0.05.
- Tabla 29.2 codificada como datos (`TECHNIQUE_TRADE_OFFS`).
- `recommend_technique(query_shape)` mapea perfiles de query a la técnica recomendada.
- Implementación mínima de BM25 (sin dependencias externas).

## API pública

| Módulo | Símbolos |
|---|---|
| `src.bm25` | `BM25Index` |
| `src.retrieval_techniques` | `Document`, `BaselineDenseRetriever`, `HyDERetriever`, `QueryRewriter`, `MultiQueryRetriever`, `HybridSearcher`, `CrossEncoderReranker`, `ParentChildChunker`, `ParentChildIndex`, `SentenceWindowRetriever`, `SelfRAGRetriever`, `reciprocal_rank_fusion` |
| `src.retrieval_evaluator` | `JUSTIFICATION_THRESHOLD_NDCG`, `ndcg_at_k`, `mrr_at_k`, `map_at_k`, `ComparisonReport`, `evaluate_technique` |
| `src.trade_offs` | `QueryShape`, `TradeOff`, `TECHNIQUE_TRADE_OFFS`, `recommend_technique` |

## El gate de justificación

Cualquier técnica avanzada añade coste (LLM calls, latencia, índices extra). El gate del manual obliga a demostrar que ese coste compra calidad real:

```python
from src.retrieval_evaluator import evaluate_technique

report = evaluate_technique(baseline_retriever, advanced_retriever, qrels, top_k=5)
assert report.justified, (
    f"HyDE no justifica su coste: ΔNDCG@5={report.delta_ndcg:.3f} < 0.05 "
    f"(+{report.latency_overhead_ms} ms, +{report.llm_calls_overhead} LLM calls)"
)
```

## Referencias del manual

- Cap. 29 — Retrieval avanzado y testing (pp. 82–83)
- Tabla 29.1 — 8 técnicas con casos de uso
- Tabla 29.2 — Trade-offs típicos (latencia, coste, mejora de recall)
- §29.3 — Gate ΔNDCG@5 ≥ +0.05
