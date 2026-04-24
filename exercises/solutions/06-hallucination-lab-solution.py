"""
Solución módulo 06: implementa un RAG Triad simplificado combinando
context_relevance + groundedness + answer_relevance en un score compuesto.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "modules" / "06-hallucination-lab"))
from src.groundedness_checker import GroundednessChecker


def context_relevance(query: str, context: list[str]) -> float:
    q_tokens = {w.lower() for w in query.split() if len(w) > 3}
    ctx_tokens = {w.lower() for chunk in context for w in chunk.split() if len(w) > 3}
    if not q_tokens:
        return 1.0
    return round(len(q_tokens & ctx_tokens) / len(q_tokens), 3)


def rag_triad(query: str, response: str, context: list[str]) -> dict[str, float]:
    checker = GroundednessChecker(overlap_threshold=0.4)
    groundedness = checker.check(response, context).score
    ctx_rel = context_relevance(query, context)
    q_tokens = {w.lower() for w in query.split() if len(w) > 3}
    r_tokens = {w.lower() for w in response.split() if len(w) > 3}
    answer_rel = round(min(1.0, len(q_tokens & r_tokens) / max(len(q_tokens), 1) * 2), 3)
    return {
        "context_relevance": ctx_rel,
        "groundedness": groundedness,
        "answer_relevance": answer_rel,
        "composite": round((ctx_rel + groundedness + answer_rel) / 3, 3),
    }


if __name__ == "__main__":
    result = rag_triad(
        query="What is the return policy?",
        response="Returns are allowed within 30 days for a full refund.",
        context=["Our return policy allows returns within 30 days."],
    )
    for k, v in result.items():
        print(f"  {k}: {v:.3f}")
