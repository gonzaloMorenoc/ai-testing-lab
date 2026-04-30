from __future__ import annotations

import math
from dataclasses import dataclass


def ndcg_at_k(relevant_ids: set[int], ranked_ids: list[int], k: int) -> float:
    """Normalized Discounted Cumulative Gain @ k.

    DCG = sum_{i=1}^{k} rel_i / log2(i+1)  where rel_i = 1 if ranked_ids[i-1] in relevant_ids
    IDCG = optimal DCG (all relevant docs ranked first)
    NDCG = DCG / IDCG
    Returns 0.0 if no relevant docs exist or k <= 0.
    """
    if k <= 0 or not relevant_ids:
        return 0.0

    top_k = ranked_ids[:k]
    dcg = sum(1.0 / math.log2(i + 2) for i, doc_id in enumerate(top_k) if doc_id in relevant_ids)

    num_ideal = min(len(relevant_ids), k)
    idcg = sum(1.0 / math.log2(i + 2) for i in range(num_ideal))

    if idcg == 0.0:
        return 0.0
    return dcg / idcg


def mrr_at_k(relevant_ids: set[int], ranked_ids: list[int], k: int) -> float:
    """Mean Reciprocal Rank @ k.

    For a single query: 1/rank of the first relevant document in top-k.
    Returns 0.0 if none of the top-k documents are relevant.
    """
    if k <= 0 or not relevant_ids:
        return 0.0

    for i, doc_id in enumerate(ranked_ids[:k]):
        if doc_id in relevant_ids:
            return 1.0 / (i + 1)
    return 0.0


def map_at_k(relevant_ids: set[int], ranked_ids: list[int], k: int) -> float:
    """Average Precision @ k for a single query.

    AP@k = (1/|R|) * sum_{i=1}^{k} P@i * rel_i
    where |R| = min(len(relevant_ids), k) for normalisation,
    P@i = precision at position i,
    rel_i = 1 if ranked_ids[i-1] in relevant_ids.
    Returns 0.0 if no relevant docs exist.
    """
    if k <= 0 or not relevant_ids:
        return 0.0

    num_relevant = min(len(relevant_ids), k)
    hits = 0
    precision_sum = 0.0

    for i, doc_id in enumerate(ranked_ids[:k]):
        if doc_id in relevant_ids:
            hits += 1
            precision_sum += hits / (i + 1)

    return precision_sum / num_relevant


@dataclass(frozen=True)
class RetrievalMetricsReport:
    ndcg: float  # NDCG@k averaged over all queries
    mrr: float  # MRR@k averaged over all queries
    map_score: float  # MAP@k averaged over all queries
    k: int
    num_queries: int
    passed: bool  # True if ndcg >= threshold AND mrr >= threshold AND map_score >= threshold


RETRIEVAL_THRESHOLD = 0.5


def evaluate_retrieval(
    relevant_sets: list[set[int]],
    ranked_lists: list[list[int]],
    k: int = 10,
    threshold: float = RETRIEVAL_THRESHOLD,
) -> RetrievalMetricsReport:
    """Evaluate retrieval quality over N queries.

    Args:
        relevant_sets: list of sets of relevant IDs, one per query
        ranked_lists: list of ranked ID lists (descending score), one per query
        k: cutoff
        threshold: minimum score for passed=True

    Raises:
        ValueError if lengths differ or inputs are empty
    """
    if len(relevant_sets) != len(ranked_lists):
        raise ValueError(
            f"relevant_sets y ranked_lists deben tener igual longitud, "
            f"got {len(relevant_sets)} vs {len(ranked_lists)}"
        )
    if not relevant_sets:
        raise ValueError("Se requiere al menos una query")

    n = len(relevant_sets)
    avg_ndcg = (
        sum(ndcg_at_k(r, ranked, k) for r, ranked in zip(relevant_sets, ranked_lists, strict=False))
        / n
    )
    avg_mrr = (
        sum(mrr_at_k(r, ranked, k) for r, ranked in zip(relevant_sets, ranked_lists, strict=False))
        / n
    )
    avg_map = (
        sum(map_at_k(r, ranked, k) for r, ranked in zip(relevant_sets, ranked_lists, strict=False))
        / n
    )

    return RetrievalMetricsReport(
        ndcg=avg_ndcg,
        mrr=avg_mrr,
        map_score=avg_map,
        k=k,
        num_queries=n,
        passed=avg_ndcg >= threshold and avg_mrr >= threshold and avg_map >= threshold,
    )
