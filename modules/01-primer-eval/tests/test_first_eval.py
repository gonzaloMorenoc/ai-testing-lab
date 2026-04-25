"""
Módulo 01 — Primer Eval con DeepEval
=====================================

Tests del laboratorio. Dos niveles:

1. Tests determinísticos (sin LLM, sin API keys) — corren siempre en CI
   Usan SimpleAnswerRelevancyMetric y SimpleFaithfulnessMetric.

2. Tests reales (@pytest.mark.slow) — requieren GROQ_API_KEY o OLLAMA
   Usan AnswerRelevancyMetric y FaithfulnessMetric de DeepEval con juez LLM real.

Ejecutar:
    pytest tests/ -v -m "not slow" --record-mode=none   # CI / sin API key
    pytest tests/ -v -m "slow"                           # con GROQ_API_KEY
"""
from __future__ import annotations

import os

import pytest
from deepeval.test_case import LLMTestCase

from src.metrics import SimpleAnswerRelevancyMetric, SimpleFaithfulnessMetric
from src.simple_rag import SimpleRAG

# ── Helpers ────────────────────────────────────────────────────────────────


def run_rag(rag: SimpleRAG, query: str) -> LLMTestCase:
    """Ejecuta el RAG y devuelve un LLMTestCase listo para evaluar."""
    actual_output, context = rag.query(query)
    return LLMTestCase(
        input=query,
        actual_output=actual_output,
        retrieval_context=context,
    )


# ── Tests determinísticos (CI, sin API keys) ───────────────────────────────


class TestAnswerRelevancy:
    """Tests de relevancia de respuesta usando métrica heurística."""

    def test_returns_query_is_relevant(self, rag: SimpleRAG) -> None:
        """Una pregunta sobre devoluciones obtiene una respuesta sobre devoluciones."""
        test_case = run_rag(rag, "What is the return policy?")
        metric = SimpleAnswerRelevancyMetric(threshold=0.5)

        metric.measure(test_case)

        print(f"\n  Score: {metric.score}")
        print(f"  Reason: {metric.reason}")
        assert metric.is_successful(), (
            f"Relevancy too low: {metric.score:.2f} < {metric.threshold} | {metric.reason}"
        )

    def test_shipping_query_is_relevant(self, rag: SimpleRAG) -> None:
        """Una pregunta sobre envíos obtiene una respuesta sobre envíos."""
        test_case = run_rag(rag, "How long does shipping take?")
        metric = SimpleAnswerRelevancyMetric(threshold=0.4)

        metric.measure(test_case)

        print(f"\n  Score: {metric.score}")
        print(f"  Reason: {metric.reason}")
        assert metric.is_successful(), (
            f"Relevancy too low: {metric.score:.2f} < {metric.threshold} | {metric.reason}"
        )

    def test_irrelevant_output_fails(self, rag: SimpleRAG) -> None:
        """Una respuesta completamente fuera de tema debe fallar la métrica."""
        test_case = LLMTestCase(
            input="What is the return policy?",
            actual_output="The weather in Madrid is sunny today.",
            retrieval_context=["Returns allowed within 30 days."],
        )
        metric = SimpleAnswerRelevancyMetric(threshold=0.5)

        metric.measure(test_case)

        print(f"\n  Score: {metric.score} (esperamos que falle la métrica)")
        assert not metric.is_successful(), (
            "La métrica debería detectar que la respuesta es irrelevante"
        )


class TestFaithfulness:
    """Tests de fidelidad al contexto usando métrica heurística."""

    def test_response_is_faithful_to_context(self, rag: SimpleRAG) -> None:
        """La respuesta del RAG debe estar fundamentada en el contexto recuperado."""
        test_case = run_rag(rag, "What is the return policy?")
        metric = SimpleFaithfulnessMetric(threshold=0.7)

        metric.measure(test_case)

        print(f"\n  Score: {metric.score}")
        print(f"  Reason: {metric.reason}")
        assert metric.is_successful(), (
            f"Faithfulness too low: {metric.score:.2f} < {metric.threshold} | {metric.reason}"
        )

    def test_hallucination_fails_faithfulness(self, hallucination_output: str, rag: SimpleRAG) -> None:
        """Una respuesta inventada debe fallar la métrica de fidelidad."""
        _, context = rag.query("What is the return policy?")
        test_case = LLMTestCase(
            input="What is the return policy?",
            actual_output=hallucination_output,
            retrieval_context=context,
        )
        metric = SimpleFaithfulnessMetric(threshold=0.7)

        metric.measure(test_case)

        print(f"\n  Score: {metric.score} (esperamos que falle la métrica)")
        assert not metric.is_successful(), (
            "La métrica debería detectar la alucinación (términos no presentes en el contexto)"
        )

    def test_no_context_gives_zero_faithfulness(self) -> None:
        """Sin contexto de recuperación, la fidelidad es 0."""
        test_case = LLMTestCase(
            input="What is the return policy?",
            actual_output="Returns are allowed within 30 days.",
            retrieval_context=[],
        )
        metric = SimpleFaithfulnessMetric(threshold=0.5)

        metric.measure(test_case)

        assert metric.score == 0.0, "Sin contexto, score debe ser 0"
        assert not metric.is_successful()


class TestBothMetrics:
    """Tests que combinan ambas métricas, como haría DeepEval en producción."""

    def test_good_response_passes_both_metrics(self, rag: SimpleRAG) -> None:
        """Una buena respuesta RAG debe pasar relevancia Y fidelidad."""
        test_case = run_rag(rag, "What is the return policy?")

        relevancy = SimpleAnswerRelevancyMetric(threshold=0.5)
        faithfulness = SimpleFaithfulnessMetric(threshold=0.7)

        relevancy.measure(test_case)
        faithfulness.measure(test_case)

        print(f"\n  AnswerRelevancy: {relevancy.score:.2f} (threshold: {relevancy.threshold})")
        print(f"  Faithfulness:    {faithfulness.score:.2f} (threshold: {faithfulness.threshold})")

        assert relevancy.is_successful(), f"Relevancy failed: {relevancy.reason}"
        assert faithfulness.is_successful(), f"Faithfulness failed: {faithfulness.reason}"


# ── Tests reales (requieren GROQ_API_KEY) ──────────────────────────────────


@pytest.mark.slow
@pytest.mark.vcr("groq_eval_example.yaml")
def test_with_real_deepeval_metrics(rag: SimpleRAG) -> None:
    """
    Test con métricas reales de DeepEval (LLM-as-judge vía Groq).

    Requiere: GROQ_API_KEY en el entorno.
    En CI: se omite con `-m "not slow"`.
    Local con cassette: pytest --record-mode=none (usa groq_eval_example.yaml).
    Local en vivo: pytest -m slow (hace llamadas reales a Groq).
    """
    if not os.getenv("GROQ_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        pytest.skip("No API key found (GROQ_API_KEY or OPENAI_API_KEY). Use -m 'not slow' for CI.")

    from deepeval import assert_test
    from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric

    test_case = run_rag(rag, "What is the return policy?")

    assert_test(test_case, [
        AnswerRelevancyMetric(threshold=0.7),
        FaithfulnessMetric(threshold=0.8),
    ])
