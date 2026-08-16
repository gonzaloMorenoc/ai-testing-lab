from __future__ import annotations

import os

import pytest

from src.dag_metric import DAGResult, build_compound_dag, build_keyword_dag
from src.geval_judge import GEvalJudge, GEvalResult


class TestGEvalRelevancy:
    def test_relevant_response_passes(self, judge: GEvalJudge, relevant_response: str) -> None:
        result: GEvalResult = judge.evaluate(relevant_response, "relevancy")
        print(f"\n  {result}")
        assert result.passed, f"Respuesta relevante debería pasar: {result.reason}"

    def test_off_topic_fails_relevancy(self, judge: GEvalJudge, off_topic_response: str) -> None:
        result = judge.evaluate(off_topic_response, "relevancy")
        print(f"\n  {result}")
        assert not result.passed, "Respuesta fuera de tema no debería pasar relevancy"

    def test_score_is_in_range(self, judge: GEvalJudge, relevant_response: str) -> None:
        result = judge.evaluate(relevant_response, "relevancy")
        assert 0.0 <= result.score <= 1.0


class TestGEvalToxicity:
    def test_toxic_response_detected(self, judge: GEvalJudge, toxic_response: str) -> None:
        result = judge.evaluate(toxic_response, "toxicity", threshold=0.3)
        print(f"\n  {result}")
        assert result.score > 0.0, "Respuesta tóxica debería tener score > 0"

    def test_clean_response_not_toxic(self, judge: GEvalJudge, relevant_response: str) -> None:
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


# ---------------------------------------------------------------------------
# Tabla 5.1 — Sesgos de LLM-as-Judge (Manual QA AI v12, Cap 05 + Cap 28)
# ---------------------------------------------------------------------------

from src.judge_bias import (  # noqa: E402
    IAAResult,
    JudgeBiasType,
    cohen_kappa,
    detect_position_bias,
    detect_verbosity_bias,
)


class TestDetectVerbosityBias:
    def test_detected_when_long_scores_much_higher(self) -> None:
        result = detect_verbosity_bias(0.7, 0.9, length_ratio=3.0)
        assert result.detected is True
        assert result.bias_type == JudgeBiasType.VERBOSITY

    def test_not_detected_when_delta_too_small(self) -> None:
        result = detect_verbosity_bias(0.7, 0.75, length_ratio=3.0)
        assert result.detected is False

    def test_not_detected_when_ratio_too_small(self) -> None:
        # ratio ≤ 2.0 → no hay bias incluso con delta grande
        result = detect_verbosity_bias(0.5, 0.9, length_ratio=1.5)
        assert result.detected is False

    def test_severity_zero_when_not_detected(self) -> None:
        result = detect_verbosity_bias(0.7, 0.75, length_ratio=3.0)
        assert result.severity == 0.0

    def test_severity_positive_when_detected(self) -> None:
        result = detect_verbosity_bias(0.7, 0.9, length_ratio=3.0)
        assert result.severity > 0.0
        assert result.severity <= 1.0

    def test_evidence_contains_expected_fields(self) -> None:
        result = detect_verbosity_bias(0.7, 0.9, length_ratio=3.0)
        assert "length_ratio" in result.evidence
        assert "score_delta" in result.evidence


class TestDetectPositionBias:
    def test_detected_when_delta_exceeds_threshold(self) -> None:
        result = detect_position_bias(score_ab=0.8, score_ba=0.6)
        assert result.detected is True
        assert result.bias_type == JudgeBiasType.POSITION

    def test_not_detected_when_delta_below_threshold(self) -> None:
        result = detect_position_bias(score_ab=0.8, score_ba=0.82)
        assert result.detected is False

    def test_severity_zero_when_not_detected(self) -> None:
        result = detect_position_bias(score_ab=0.8, score_ba=0.82)
        assert result.severity == 0.0

    def test_severity_capped_at_one(self) -> None:
        result = detect_position_bias(score_ab=1.0, score_ba=0.0)
        assert result.severity == 1.0

    def test_evidence_contains_ab_ba_scores(self) -> None:
        result = detect_position_bias(score_ab=0.8, score_ba=0.6)
        assert "AB=" in result.evidence
        assert "BA=" in result.evidence


class TestCohenKappa:
    def test_partial_agreement_kappa_in_range(self) -> None:
        result = cohen_kappa([1, 1, 0, 1, 0], [1, 1, 0, 0, 0])
        assert 0.41 <= result.score <= 1.0
        assert result.n_items == 5

    def test_perfect_agreement_kappa_one(self) -> None:
        result = cohen_kappa([1, 1, 1, 1], [1, 1, 1, 1])
        assert result.score == 1.0
        assert result.high_quality is True

    def test_total_disagreement_kappa_negative_or_low(self) -> None:
        result = cohen_kappa([1, 0, 1, 0], [0, 1, 0, 1])
        assert result.acceptable is False

    def test_acceptable_property_true_above_threshold(self) -> None:
        # score=0.65 → acceptable
        result = IAAResult(
            metric_name="cohen_kappa", score=0.65, n_items=10, interpretation="sustancial"
        )
        assert result.acceptable is True

    def test_acceptable_property_false_below_threshold(self) -> None:
        result = IAAResult(
            metric_name="cohen_kappa", score=0.50, n_items=10, interpretation="moderado"
        )
        assert result.acceptable is False

    def test_high_quality_property_true_above_threshold(self) -> None:
        result = IAAResult(
            metric_name="cohen_kappa", score=0.85, n_items=10, interpretation="casi perfecto"
        )
        assert result.high_quality is True

    def test_high_quality_property_false_below_threshold(self) -> None:
        result = IAAResult(
            metric_name="cohen_kappa", score=0.75, n_items=10, interpretation="sustancial"
        )
        assert result.high_quality is False

    def test_raises_on_length_mismatch(self) -> None:
        with pytest.raises(ValueError):
            cohen_kappa([1, 0, 1], [1, 0])

    def test_raises_on_empty_lists(self) -> None:
        with pytest.raises(ValueError):
            cohen_kappa([], [])

    def test_n_items_matches_input_length(self) -> None:
        result = cohen_kappa([1, 1, 0, 1, 0], [1, 1, 0, 0, 0])
        assert result.n_items == 5

    def test_metric_name_is_cohen_kappa(self) -> None:
        result = cohen_kappa([1, 1, 1], [1, 1, 1])
        assert result.metric_name == "cohen_kappa"


class TestJudgeBiasTypeEnum:
    def test_verbosity_value(self) -> None:
        assert JudgeBiasType.VERBOSITY.value == "verbosity"

    def test_all_five_biases_defined(self) -> None:
        expected = {"verbosity", "self_enhancement", "position", "lenient", "format"}
        actual = {b.value for b in JudgeBiasType}
        assert actual == expected


class TestGEvalCompare:
    """compare() puntua cada salida por separado y decide el ganador."""

    def test_relevant_beats_off_topic(
        self, judge: GEvalJudge, relevant_response: str, off_topic_response: str
    ) -> None:
        result = judge.compare(relevant_response, off_topic_response, "relevancy")
        assert result["winner"] == "A"
        assert result["score_a"] > result["score_b"]

    def test_winner_follows_the_content_not_the_position(
        self, judge: GEvalJudge, relevant_response: str, off_topic_response: str
    ) -> None:
        result = judge.compare(off_topic_response, relevant_response, "relevancy")
        assert result["winner"] == "B", (
            "La respuesta relevante debe ganar tambien en segunda posicion"
        )

    def test_identical_outputs_tie(self, judge: GEvalJudge, relevant_response: str) -> None:
        result = judge.compare(relevant_response, relevant_response, "relevancy")
        assert result["winner"] == "tie"
        assert result["score_a"] == result["score_b"]

    def test_scores_match_standalone_evaluate(
        self, judge: GEvalJudge, relevant_response: str, off_topic_response: str
    ) -> None:
        result = judge.compare(relevant_response, off_topic_response, "relevancy")
        assert result["score_a"] == judge.evaluate(relevant_response, "relevancy").score
        assert result["score_b"] == judge.evaluate(off_topic_response, "relevancy").score


class TestCalibrateForPositionBias:
    """Evalua el par en ambos ordenes y promedia, para neutralizar el sesgo de posicion."""

    def test_calibrated_scores_match_standalone_evaluate(
        self, judge: GEvalJudge, relevant_response: str, off_topic_response: str
    ) -> None:
        result = judge.calibrate_for_position_bias(
            relevant_response, off_topic_response, "relevancy"
        )
        assert result["calibrated_score_a"] == pytest.approx(
            judge.evaluate(relevant_response, "relevancy").score
        )
        assert result["calibrated_score_b"] == pytest.approx(
            judge.evaluate(off_topic_response, "relevancy").score
        )

    def test_keyword_judge_is_immune_to_position_bias(
        self, judge: GEvalJudge, relevant_response: str, off_topic_response: str
    ) -> None:
        """Este juez puntua por keywords, sin ver la otra respuesta: el orden no le afecta.

        Es la leccion del modulo: un juez LLM real si mueve la nota al invertir
        el orden, y por eso hay que calibrar. Este no, y el test lo deja explicito.
        """
        result = judge.calibrate_for_position_bias(
            relevant_response, off_topic_response, "relevancy"
        )
        assert result["bias_delta"] == 0.0
        assert result["bias_detected"] is False

    def test_calibrated_winner_is_the_better_answer(
        self, judge: GEvalJudge, relevant_response: str, off_topic_response: str
    ) -> None:
        assert (
            judge.calibrate_for_position_bias(relevant_response, off_topic_response, "relevancy")[
                "calibrated_winner"
            ]
            == "A"
        )
        assert (
            judge.calibrate_for_position_bias(off_topic_response, relevant_response, "relevancy")[
                "calibrated_winner"
            ]
            == "B"
        )

    def test_calibrated_winner_ties_on_identical_outputs(
        self, judge: GEvalJudge, relevant_response: str
    ) -> None:
        result = judge.calibrate_for_position_bias(
            relevant_response, relevant_response, "relevancy"
        )
        assert result["calibrated_winner"] == "tie"
        assert result["bias_detected"] is False
