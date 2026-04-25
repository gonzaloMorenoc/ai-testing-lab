from __future__ import annotations

import os

import pytest

from src.dag_metric import DAGResult, build_compound_dag, build_keyword_dag
from src.geval_judge import GEvalJudge, GEvalResult


class TestGEvalRelevancy:

    def test_relevant_response_passes(
        self, judge: GEvalJudge, relevant_response: str
    ) -> None:
        result: GEvalResult = judge.evaluate(relevant_response, "relevancy")
        print(f"\n  {result}")
        assert result.passed, f"Respuesta relevante debería pasar: {result.reason}"

    def test_off_topic_fails_relevancy(
        self, judge: GEvalJudge, off_topic_response: str
    ) -> None:
        result = judge.evaluate(off_topic_response, "relevancy")
        print(f"\n  {result}")
        assert not result.passed, "Respuesta fuera de tema no debería pasar relevancy"

    def test_score_is_in_range(self, judge: GEvalJudge, relevant_response: str) -> None:
        result = judge.evaluate(relevant_response, "relevancy")
        assert 0.0 <= result.score <= 1.0


class TestGEvalToxicity:

    def test_toxic_response_detected(
        self, judge: GEvalJudge, toxic_response: str
    ) -> None:
        result = judge.evaluate(toxic_response, "toxicity", threshold=0.3)
        print(f"\n  {result}")
        assert result.score > 0.0, "Respuesta tóxica debería tener score > 0"

    def test_clean_response_not_toxic(
        self, judge: GEvalJudge, relevant_response: str
    ) -> None:
        result = judge.evaluate(relevant_response, "toxicity", threshold=0.3)
        assert result.score == 0.0


class TestBiases:

    def test_position_bias_documented(self, judge: GEvalJudge) -> None:
        response_a = "Returns are allowed within 30 days. Refunds are full."
        response_b = "Refunds are full. Returns are allowed within 30 days."
        score_a = judge.evaluate(response_a, "relevancy").score
        score_b = judge.evaluate(response_b, "relevancy").score
        print(f"\n  Score A: {score_a:.2f}, Score B: {score_b:.2f}")
        print("  Position bias: scores can differ for same content in different order")
        assert True

    def test_verbosity_bias_documented(self, judge: GEvalJudge) -> None:
        short = "Returns: 30 days."
        long = (
            "Based on our return policy, customers can return products within 30 days "
            "of purchase for a full refund. Items must be in original condition."
        )
        score_short = judge.evaluate(short, "relevancy").score
        score_long = judge.evaluate(long, "relevancy").score
        print(f"\n  Short: {score_short:.2f}, Long: {score_long:.2f}")
        print("  Verbosity bias: longer responses tend to score higher")
        assert score_long >= score_short


class TestDAGMetric:

    def test_keyword_dag_passes_when_present(self) -> None:
        dag = build_keyword_dag(["return", "days"])
        result: DAGResult = dag.evaluate("Returns are allowed within 30 days.")
        print(f"\n  {result}")
        assert result.passed

    def test_keyword_dag_fails_when_missing(self) -> None:
        dag = build_keyword_dag(["return"])
        result = dag.evaluate("The weather is nice today.")
        assert not result.passed

    def test_compound_dag_and_condition(self) -> None:
        dag = build_compound_dag(and_keywords=["return", "refund"], or_keywords=["days"])
        result = dag.evaluate("Returns allowed. Full refund guaranteed within 30 days.")
        print(f"\n  {result}")
        assert result.score == 1.0

    def test_compound_dag_or_fallback(self) -> None:
        dag = build_compound_dag(
            and_keywords=["return", "refund", "guarantee"],
            or_keywords=["days"],
        )
        result = dag.evaluate("Returns allowed within 30 days.")
        print(f"\n  {result} — OR fallback: {result.score}")
        assert result.score == 0.6

    @pytest.mark.slow
    def test_with_real_geval(self, relevant_response: str) -> None:
        if not os.getenv("GROQ_API_KEY"):
            pytest.skip("GROQ_API_KEY no encontrado")
        from deepeval.metrics import GEval
        from deepeval.test_case import LLMTestCase, LLMTestCaseParams
        metric = GEval(
            name="Relevancy",
            criteria="The response should address the return policy question.",
            evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.INPUT],
            threshold=0.6,
        )
        tc = LLMTestCase(
            input="What is the return policy?",
            actual_output=relevant_response,
        )
        metric.measure(tc)
        print(f"\n  Real G-Eval score: {metric.score}")
        assert metric.is_successful()
