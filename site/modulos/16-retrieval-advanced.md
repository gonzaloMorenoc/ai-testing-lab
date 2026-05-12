---
title: "16 — retrieval-advanced"
---

# 16 — retrieval-advanced

Un retriever k-NN sobre embeddings densos es la versión mínima viable de un RAG. Producción real exige técnicas avanzadas que mejoran la calidad de los chunks recuperados, especialmente para queries ambiguas, multi-hop o de dominio especializado.

## El problema

Tu RAG funciona bien sobre queries largas y bien formuladas, pero falla en cuatro escenarios:

1. **Queries cortas o ambiguas** ("¿qué pasa con eso?") — un retriever denso no sabe qué expandir.
2. **Jerga muy específica** — los embeddings densos no recogen códigos de producto, números o identificadores.
3. **Posición top-1 importa** — el embedder coloca el doc relevante en posición 3, no en posición 1.
4. **Documentos largos y estructurados** — recuperar un chunk pequeño deja al LLM sin contexto suficiente.

El **Capítulo 29 del manual v13** cataloga 8 técnicas para resolver estos casos y propone el gate canónico: ninguna técnica entra en producción sin demostrar **ΔNDCG@5 ≥ +0.05** sobre la baseline.

## Cómo funciona

### 8 técnicas, una API uniforme

Todas las técnicas exponen `retrieve(query, top_k) -> list[Document]` y `cost_overhead() -> dict[str, float]`. Esto permite tratarlas intercambiablemente en CI y compararlas con la misma batería de tests.

| Técnica | Cuándo usar | Coste extra |
|---|---|---|
| `HyDERetriever` | Queries cortas o ambiguas | +1 LLM call · +350 ms |
| `QueryRewriter` | Queries conversacionales o con jerga | +1 LLM call · +225 ms |
| `MultiQueryRetriever(N=3)` | Cobertura de aspectos múltiples | +N retrievals · +150 ms |
| `HybridSearcher` | Documentación técnica con jerga específica | +BM25 index · +75 ms |
| `CrossEncoderReranker` | Cuando la posición top-1 importa | +1 model call · +200 ms |
| `ParentChildChunker` | Documentos largos estructurados | +50 ms |
| `SentenceWindowRetriever` | Cuando el contexto local importa | +50 ms |
| `SelfRAGRetriever` | Tareas que requieren razonamiento iterativo | +2 LLM calls · +400 ms |

### El gate de justificación (§29.3)

```python
from src.retrieval_evaluator import evaluate_technique

report = evaluate_technique(baseline, advanced, qrels_by_query, top_k=5)

# Gate canónico del manual: una técnica solo se justifica si mejora NDCG@5 al menos +0.05
assert report.justified, (
    f"Técnica no justifica su coste: "
    f"ΔNDCG@5={report.delta_ndcg:.3f}, +{report.latency_overhead_ms} ms"
)
```

Este gate vive en `JUSTIFICATION_THRESHOLD_NDCG = 0.05` (módulo `retrieval_evaluator`).

### Métricas IR canónicas

```python
from src.retrieval_evaluator import ndcg_at_k, mrr_at_k, map_at_k

retrieved = ["d3", "d1", "d7", "d2", "d5"]
qrels = {"d1": 2.0, "d3": 1.0, "d5": 1.0}

print(ndcg_at_k(retrieved, qrels, k=5))  # 0.91
print(mrr_at_k(retrieved, qrels, k=5))   # 1.0 (d3 está en posición 1)
print(map_at_k(retrieved, qrels, k=5))   # 0.81
```

### Recomendar técnica por perfil de query

```python
from src.trade_offs import QueryShape, recommend_technique

assert recommend_technique(QueryShape.SHORT_AMBIGUOUS) == "hyde"
assert recommend_technique(QueryShape.DOMAIN_JARGON) == "hybrid_search"
assert recommend_technique(QueryShape.POSITION_CRITICAL) == "reranking"
```

## Hybrid search: BM25 + denso fusionado con RRF

`HybridSearcher` combina retrievaal léxico (BM25) y semántico (embeddings densos) usando **Reciprocal Rank Fusion** (k=60). La fusión RRF es resistente a outliers de score y no requiere normalización entre los dos rankings.

```python
from src.retrieval_techniques import HybridSearcher

searcher = HybridSearcher(docs)
results = searcher.retrieve("paella valenciana", top_k=5)
# Encuentra docs con "paella" exacto (BM25) + relacionados ("arroz", "azafrán") (denso)
```

## Integración con la Tabla 4.2

Las métricas operativas del retriever (`context_recall`, `context_precision`) están en `qa_thresholds.py` raíz:

```python
from qa_thresholds import QA_THRESHOLDS, RiskLevel

threshold = QA_THRESHOLDS["context_recall"]
assert threshold.gate(recall_score, RiskLevel.TARGET)  # ≥ 0.85 objetivo
```

## Referencias

- Manual QA AI v13 — Cap. 29 (pp. 82–83), Tablas 29.1 y 29.2
- Gao et al. 2022 — Precise Zero-Shot Dense Retrieval (HyDE)
- Pradeep et al. 2021 — Expando-Mono-Duo Design Pattern (reranking)
- Asai et al. 2023 — Self-RAG
- Robertson 1994 — BM25
