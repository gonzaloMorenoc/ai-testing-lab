"""Tests de los gates por etapa (D.5)."""

import pytest

from gates_pipeline import GATES, Stage, evaluate_stage


class TestGatesStructure:
    def test_four_stages_defined(self):
        assert set(GATES.keys()) == set(Stage)

    def test_pr_target_lower_than_pre_staging(self):
        pr_faith = GATES[Stage.PULL_REQUEST]["faithfulness_min"]
        staging_faith = GATES[Stage.PRE_STAGING]["faithfulness_min"]
        assert staging_faith > pr_faith

    def test_unknown_stage_raises(self):
        with pytest.raises(KeyError):
            evaluate_stage("nonexistent", {})  # type: ignore[arg-type]


class TestPullRequestGate:
    def test_passes_with_good_metrics(self):
        result = evaluate_stage(
            Stage.PULL_REQUEST,
            {"faithfulness": 0.88, "consistency": 0.82, "cost_delta": 0.05},
        )
        assert result.passed
        assert result.failed_gates == ()

    def test_fails_when_faithfulness_below(self):
        result = evaluate_stage(
            Stage.PULL_REQUEST,
            {"faithfulness": 0.80, "consistency": 0.82, "cost_delta": 0.05},
        )
        assert not result.passed
        assert any("faithfulness" in g for g in result.failed_gates)

    def test_fails_when_cost_exceeds_delta(self):
        result = evaluate_stage(
            Stage.PULL_REQUEST,
            {"faithfulness": 0.88, "consistency": 0.82, "cost_delta": 0.15},
        )
        assert not result.passed

    def test_missing_data_marks_no_data(self):
        result = evaluate_stage(
            Stage.PULL_REQUEST,
            {"faithfulness": 0.88},  # falta consistency y cost_delta
        )
        assert not result.passed
        assert any("no_data" in g for g in result.failed_gates)


class TestPreStagingGate:
    def test_passes_release_v3_3_metrics(self):
        # D.11: v3.3 faithfulness 0.93, consistency 0.84, etc.
        observed = {
            "faithfulness": 0.93,
            "answer_correctness": 0.89,
            "context_recall": 0.87,
            "ndcg_at_5": 0.82,
            "safety_canary_leaks": 0.0,
        }
        result = evaluate_stage(Stage.PRE_STAGING, observed)
        assert result.passed

    def test_fails_with_incident_metrics(self):
        # D.8: durante el incidente, faithfulness cae a 0.76
        observed = {
            "faithfulness": 0.76,
            "answer_correctness": 0.80,
            "context_recall": 0.87,
            "ndcg_at_5": 0.82,
            "safety_canary_leaks": 0.0,
        }
        result = evaluate_stage(Stage.PRE_STAGING, observed)
        assert not result.passed


class TestCanaryGate:
    def test_auto_rollback_when_below_threshold(self):
        result = evaluate_stage(
            Stage.CANARY_1_PCT, {"faithfulness": 0.75, "auto_rollback": 0.75}
        )
        assert not result.passed
        # Mensaje específico de auto-rollback
        assert any("auto_rollback" in g or "faithfulness" in g for g in result.failed_gates)
