"""Evaluación de técnicas de retrieval avanzado contra baseline.

Métricas IR: NDCG@k, MRR@k, MAP@k. Implementación interna determinista para
evitar dependencia obligatoria de ranx (que sigue siendo opcional para
proyectos que quieran sustituir nuestra implementación).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from retrieval_techniques import Document

# Gate del manual §29.3: una técnica avanzada solo se justifica si mejora
# NDCG@5 al menos +0.05 sobre la baseline.
JUSTIFICATION_THRESHOLD_NDCG = 0.05


def _dcg(relevances: list[float]) -> float:
    return sum(r / math.log2(i + 2) for i, r in enumerate(relevances))


def ndcg_at_k(
    retrieved: list[str], qrels: dict[str, float], k: int = 5
) -> float:
    """NDCG@k. qrels: doc_id -> relevancia (0/1 o 0/1/2/3...)."""
    retrieved_top = retrieved[:k]
    rels = [qrels.get(doc_id, 0.0) for doc_id in retrieved_top]
    ideal = sorted(qrels.values(), reverse=True)[:k]
    dcg = _dcg(rels)
    idcg = _dcg(ideal)
    if idcg == 0:
        return 0.0
    return dcg / idcg


def mrr_at_k(retrieved: list[str], qrels: dict[str, float], k: int = 5) -> float:
    """Mean Reciprocal Rank: 1 / posición del primer relevante."""
    for i, doc_id in enumerate(retrieved[:k]):
        if qrels.get(doc_id, 0.0) > 0:
            return 1.0 / (i + 1)
    return 0.0


def map_at_k(retrieved: list[str], qrels: dict[str, float], k: int = 5) -> float:
    """Mean Average Precision @ k."""
    relevant_count = 0
    precisions: list[float] = []
    for i, doc_id in enumerate(retrieved[:k]):
        if qrels.get(doc_id, 0.0) > 0:
            relevant_count += 1
            precisions.append(relevant_count / (i + 1))
    total_relevant = sum(1 for v in qrels.values() if v > 0)
    if total_relevant == 0:
        return 0.0
    return sum(precisions) / min(total_relevant, k) if precisions else 0.0


@dataclass(frozen=True)
class ComparisonReport:
    """Resultado de comparar baseline vs técnica avanzada."""

    baseline_ndcg5: float
    advanced_ndcg5: float
    delta_ndcg: float
    baseline_mrr5: float
    advanced_mrr5: float
    delta_mrr: float
    baseline_map5: float
    advanced_map5: float
    delta_map: float
    latency_overhead_ms: float
    llm_calls_overhead: float
    justified: bool

    @classmethod
    def from_scores(
        cls,
        baseline_scores: dict[str, float],
        advanced_scores: dict[str, float],
        baseline_overhead: dict[str, float],
        advanced_overhead: dict[str, float],
    ) -> ComparisonReport:
        b_ndcg = baseline_scores.get("ndcg5", 0.0)
        a_ndcg = advanced_scores.get("ndcg5", 0.0)
        b_mrr = baseline_scores.get("mrr5", 0.0)
        a_mrr = advanced_scores.get("mrr5", 0.0)
        b_map = baseline_scores.get("map5", 0.0)
        a_map = advanced_scores.get("map5", 0.0)
        delta_ndcg = a_ndcg - b_ndcg
        return cls(
            baseline_ndcg5=b_ndcg,
            advanced_ndcg5=a_ndcg,
            delta_ndcg=delta_ndcg,
            baseline_mrr5=b_mrr,
            advanced_mrr5=a_mrr,
            delta_mrr=a_mrr - b_mrr,
            baseline_map5=b_map,
            advanced_map5=a_map,
            delta_map=a_map - b_map,
            latency_overhead_ms=advanced_overhead.get("latency_ms", 0.0)
            - baseline_overhead.get("latency_ms", 0.0),
            llm_calls_overhead=advanced_overhead.get("llm_calls", 0.0)
            - baseline_overhead.get("llm_calls", 0.0),
            justified=delta_ndcg >= JUSTIFICATION_THRESHOLD_NDCG,
        )


def evaluate_technique(
    baseline_retriever,
    advanced_retriever,
    qrels_by_query: dict[str, dict[str, float]],
    top_k: int = 5,
) -> ComparisonReport:
    """Compara dos retrievers sobre un conjunto de queries con qrels."""

    def _avg(metric_fn, retriever) -> float:
        if not qrels_by_query:
            return 0.0
        total = 0.0
        for query, qrels in qrels_by_query.items():
            retrieved = [d.doc_id for d in retriever.retrieve(query, top_k=top_k)]
            total += metric_fn(retrieved, qrels, k=top_k)
        return total / len(qrels_by_query)

    baseline_scores = {
        "ndcg5": _avg(ndcg_at_k, baseline_retriever),
        "mrr5": _avg(mrr_at_k, baseline_retriever),
        "map5": _avg(map_at_k, baseline_retriever),
    }
    advanced_scores = {
        "ndcg5": _avg(ndcg_at_k, advanced_retriever),
        "mrr5": _avg(mrr_at_k, advanced_retriever),
        "map5": _avg(map_at_k, advanced_retriever),
    }
    return ComparisonReport.from_scores(
        baseline_scores,
        advanced_scores,
        baseline_retriever.cost_overhead(),
        advanced_retriever.cost_overhead(),
    )


# Silence unused-import warnings for type completeness
_ = Document
