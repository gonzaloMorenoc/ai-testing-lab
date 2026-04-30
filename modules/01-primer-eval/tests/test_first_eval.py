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
from src.threshold_checker import QA_THRESHOLDS, QAGateChecker, RiskLevel

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

    def test_hallucination_fails_faithfulness(
        self, hallucination_output: str, rag: SimpleRAG
    ) -> None:
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

    assert_test(
        test_case,
        [
            AnswerRelevancyMetric(threshold=0.7),
            FaithfulnessMetric(threshold=0.8),
        ],
    )


# ── Tests de QAGateChecker (Tabla 1.2 — umbrales maestros) ────────────────────


class TestQAGateChecker:
    """Verifica que QAGateChecker aplica correctamente los umbrales de la Tabla 1.2."""

    def test_score_above_high_risk_passes_standard_gate(self) -> None:
        checker = QAGateChecker(level=RiskLevel.STANDARD)
        assert checker.all_passed({"faithfulness": 0.91})

    def test_score_above_high_risk_passes_high_risk_gate(self) -> None:
        checker = QAGateChecker(level=RiskLevel.HIGH_RISK)
        assert checker.all_passed({"faithfulness": 0.91})

    def test_score_below_minimum_fails_standard_gate(self) -> None:
        checker = QAGateChecker(level=RiskLevel.STANDARD)
        assert not checker.all_passed({"faithfulness": 0.69})

    def test_score_at_target_but_below_high_risk_fails_high_risk_gate(self) -> None:
        # 0.85 >= target (0.85) pero < high_risk (0.90), debe fallar en HIGH_RISK
        checker = QAGateChecker(level=RiskLevel.HIGH_RISK)
        assert not checker.all_passed({"faithfulness": 0.85})

    def test_tier_pass_high_risk(self) -> None:
        threshold = QA_THRESHOLDS["faithfulness"]
        assert threshold.tier(0.91) == "pass_high_risk"

    def test_tier_pass_target(self) -> None:
        threshold = QA_THRESHOLDS["faithfulness"]
        assert threshold.tier(0.85) == "pass_target"

    def test_tier_pass_minimum(self) -> None:
        threshold = QA_THRESHOLDS["faithfulness"]
        assert threshold.tier(0.72) == "pass_minimum"

    def test_tier_fail(self) -> None:
        threshold = QA_THRESHOLDS["faithfulness"]
        assert threshold.tier(0.69) == "fail"

    def test_all_passed_returns_false_if_any_metric_fails(self) -> None:
        # faithfulness pasa (0.91 >= 0.70) pero answer_relevancy falla (0.70 < 0.75)
        checker = QAGateChecker(level=RiskLevel.STANDARD)
        assert not checker.all_passed({"faithfulness": 0.91, "answer_relevancy": 0.70})

    def test_unknown_metric_is_skipped(self) -> None:
        checker = QAGateChecker(level=RiskLevel.STANDARD)
        # Una métrica desconocida no debe lanzar excepción ni influir en el resultado
        assert checker.all_passed({"unknown_metric": 0.00})
