"""Tabla 29.2 del Manual v13 codificada como datos.

Trade-offs típicos por técnica: coste adicional, latencia extra, mejora de recall.
Las mejoras son aproximaciones basadas en benchmarks (Gao 2022, Pradeep 2021);
medir siempre con el propio corpus antes de decidir.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class QueryShape(StrEnum):
    SHORT_AMBIGUOUS = "short_ambiguous"
    CONVERSATIONAL = "conversational"
    MULTI_ASPECT = "multi_aspect"
    DOMAIN_JARGON = "domain_jargon"
    POSITION_CRITICAL = "position_critical"
    LARGE_STRUCTURED_DOC = "large_structured_doc"
    LOCAL_CONTEXT = "local_context"
    ITERATIVE_REASONING = "iterative_reasoning"


@dataclass(frozen=True)
class TradeOff:
    name: str
    extra_llm_calls: int
    latency_ms: float
    recall_improvement_pct: tuple[int, int]
    extra_model_calls: int = 0
    extra_retrievals: int = 0
    extra_index: str | None = None


TECHNIQUE_TRADE_OFFS: dict[str, TradeOff] = {
    "hyde": TradeOff(
        name="HyDE",
        extra_llm_calls=1,
        latency_ms=350.0,
        recall_improvement_pct=(5, 12),
    ),
    "query_rewriting": TradeOff(
        name="Query rewriting",
        extra_llm_calls=1,
        latency_ms=225.0,
        recall_improvement_pct=(3, 8),
    ),
    "multi_query_n3": TradeOff(
        name="Multi-query (N=3)",
        extra_llm_calls=0,
        latency_ms=150.0,
        recall_improvement_pct=(5, 15),
        extra_retrievals=3,
    ),
    "hybrid_search": TradeOff(
        name="Hybrid search (BM25 + dense)",
        extra_llm_calls=0,
        latency_ms=75.0,
        recall_improvement_pct=(8, 20),
        extra_index="BM25",
    ),
    "reranking": TradeOff(
        name="Cross-encoder reranking",
        extra_llm_calls=0,
        latency_ms=200.0,
        recall_improvement_pct=(10, 25),
        extra_model_calls=1,
    ),
    "parent_child": TradeOff(
        name="Parent-child chunking",
        extra_llm_calls=0,
        latency_ms=50.0,
        recall_improvement_pct=(5, 10),
    ),
    "sentence_window": TradeOff(
        name="Sentence-window",
        extra_llm_calls=0,
        latency_ms=50.0,
        recall_improvement_pct=(3, 8),
    ),
    "self_rag": TradeOff(
        name="Self-RAG",
        extra_llm_calls=2,
        latency_ms=400.0,
        recall_improvement_pct=(8, 18),
    ),
}


# Mapeo perfil → técnica recomendada (reglas del manual §29.2).
_SHAPE_RECOMMENDATIONS: dict[QueryShape, str] = {
    QueryShape.SHORT_AMBIGUOUS: "hyde",
    QueryShape.CONVERSATIONAL: "query_rewriting",
    QueryShape.MULTI_ASPECT: "multi_query_n3",
    QueryShape.DOMAIN_JARGON: "hybrid_search",
    QueryShape.POSITION_CRITICAL: "reranking",
    QueryShape.LARGE_STRUCTURED_DOC: "parent_child",
    QueryShape.LOCAL_CONTEXT: "sentence_window",
    QueryShape.ITERATIVE_REASONING: "self_rag",
}


def recommend_technique(shape: QueryShape) -> str:
    """Devuelve el id de la técnica recomendada para el perfil dado."""
    if shape not in _SHAPE_RECOMMENDATIONS:
        raise ValueError(f"shape desconocida: {shape}")
    return _SHAPE_RECOMMENDATIONS[shape]
