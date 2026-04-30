from __future__ import annotations

import pytest

from src.ci_gate_pipeline import (
    STAGE_DELTA_THRESHOLDS,
    CIGatePipeline,
    CIStage,
)


@pytest.fixture
def pipeline() -> CIGatePipeline:
    return CIGatePipeline()


# Scores que pasan PR pero no Staging
_SCORES_PASS_PR_FAIL_STAGING = {
    "faithfulness": 0.72,  # PR ≥0.70 ✓, Staging ≥0.80 ✗
    "answer_relevancy": 0.76,
    "context_recall": 0.71,
    "refusal_rate": 0.96,
}

# Scores muy altos — pasan production
_SCORES_ALL_PASS = {
    "faithfulness": 0.95,
    "answer_relevancy": 0.95,
    "context_recall": 0.95,
    "refusal_rate": 0.995,
}


class TestCIGatePipeline:
    def test_pr_gate_passes_with_good_scores(self, pipeline: CIGatePipeline) -> None:
        scores = {
            "faithfulness": 0.85,
            "answer_relevancy": 0.90,
            "context_recall": 0.80,
            "refusal_rate": 0.96,
        }
        result = pipeline.run_gate(CIStage.PR, scores)
        assert result.passed is True
        assert result.failures == ()
        assert result.regression_failures == ()
        assert result.stage == CIStage.PR

    def test_pr_gate_fails_low_faithfulness(self, pipeline: CIGatePipeline) -> None:
        scores = {
            "faithfulness": 0.65,  # below 0.70
            "answer_relevancy": 0.80,
            "context_recall": 0.75,
            "refusal_rate": 0.96,
        }
        result = pipeline.run_gate(CIStage.PR, scores)
        assert result.passed is False
        assert "faithfulness" in result.failures

    def test_staging_stricter_than_pr(self, pipeline: CIGatePipeline) -> None:
        # faithfulness=0.72 passes PR (≥0.70) but fails Staging (≥0.80)
        scores = _SCORES_PASS_PR_FAIL_STAGING
        pr_result = pipeline.run_gate(CIStage.PR, scores)
        staging_result = pipeline.run_gate(CIStage.STAGING, scores)
        assert pr_result.passed is True
        assert staging_result.passed is False
        assert "faithfulness" in staging_result.failures

    def test_production_strictest(self, pipeline: CIGatePipeline) -> None:
        # Scores good enough for Staging but not Production
        scores = {
            "faithfulness": 0.82,
            "answer_relevancy": 0.87,
            "context_recall": 0.83,
            "refusal_rate": 0.972,
        }
        staging_result = pipeline.run_gate(CIStage.STAGING, scores)
        production_result = pipeline.run_gate(CIStage.PRODUCTION, scores)
        assert staging_result.passed is True
        assert production_result.passed is False

    def test_regression_failure_detected(self, pipeline: CIGatePipeline) -> None:
        # Score above PR threshold but has a delta below -0.03 vs baseline
        scores = {"faithfulness": 0.80, "answer_relevancy": 0.85}
        baseline = {"faithfulness": 0.84, "answer_relevancy": 0.85}
        # delta = 0.80 - 0.84 = -0.04 < -0.03 → regression
        result = pipeline.run_gate(CIStage.PR, scores, baseline=baseline)
        assert result.passed is False
        assert "faithfulness" in result.regression_failures
        assert result.failures == ()  # absolute threshold still passes

    def test_no_regression_without_baseline(self, pipeline: CIGatePipeline) -> None:
        scores = {"faithfulness": 0.85, "answer_relevancy": 0.90}
        result = pipeline.run_gate(CIStage.PR, scores, baseline=None)
        assert result.regression_failures == ()

    def test_run_all_stages_returns_four(self, pipeline: CIGatePipeline) -> None:
        results = pipeline.run_all_stages(_SCORES_ALL_PASS)
        assert len(results) == 4
        stages = [r.stage for r in results]
        assert stages == [CIStage.PR, CIStage.STAGING, CIStage.CANARY, CIStage.PRODUCTION]

    def test_first_failing_stage_pr(self, pipeline: CIGatePipeline) -> None:
        scores = {
            "faithfulness": 0.50,  # fails every stage
            "answer_relevancy": 0.50,
        }
        failing = pipeline.first_failing_stage(scores)
        assert failing == CIStage.PR

    def test_first_failing_stage_none_if_all_pass(self, pipeline: CIGatePipeline) -> None:
        failing = pipeline.first_failing_stage(_SCORES_ALL_PASS)
        assert failing is None

    def test_gate_result_frozen(self, pipeline: CIGatePipeline) -> None:
        result = pipeline.run_gate(CIStage.PR, {"faithfulness": 0.85})
        with pytest.raises(AttributeError):
            result.passed = False  # type: ignore[misc]

    def test_partial_metrics_ok(self, pipeline: CIGatePipeline) -> None:
        # Only faithfulness provided — only that metric is evaluated
        scores = {"faithfulness": 0.75}
        result = pipeline.run_gate(CIStage.PR, scores)
        # answer_relevancy, context_recall, refusal_rate not in scores → not checked
        assert result.passed is True
        assert result.failures == ()

    def test_canary_delta_stricter_than_pr(self) -> None:
        pr_delta = STAGE_DELTA_THRESHOLDS[CIStage.PR]["faithfulness"]
        canary_delta = STAGE_DELTA_THRESHOLDS[CIStage.CANARY]["faithfulness"]
        # Canary allows less regression (closer to 0 means stricter)
        assert canary_delta > pr_delta

    def test_all_stages_pass_with_excellent_scores(self, pipeline: CIGatePipeline) -> None:
        results = pipeline.run_all_stages(_SCORES_ALL_PASS)
        assert all(r.passed for r in results)

    def test_baseline_stored_in_result(self, pipeline: CIGatePipeline) -> None:
        scores = {"faithfulness": 0.85}
        baseline = {"faithfulness": 0.80}
        result = pipeline.run_gate(CIStage.PR, scores, baseline=baseline)
        assert result.baseline == baseline

    def test_staging_regression_stricter_than_pr_regression(self) -> None:
        pr_delta = STAGE_DELTA_THRESHOLDS[CIStage.PR]["faithfulness"]
        staging_delta = STAGE_DELTA_THRESHOLDS[CIStage.STAGING]["faithfulness"]
        # Staging allows less regression than PR
        assert staging_delta > pr_delta
