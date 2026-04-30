"""Tests para eval_antipatterns — AP-01 .. AP-10.

Sin LLM, sin API keys.  Todos los tests son deterministas.
"""
from __future__ import annotations

import pytest

from src.eval_antipatterns import (
    AntiPatternSeverity,
    AntiPatternViolation,
    EvalDesignChecker,
    EvalDesignReport,
    check_ap01_happy_path_only,
    check_ap02_data_contamination,
    check_ap03_no_baseline,
    check_ap04_insufficient_sample_size,
    check_ap05_judge_equals_generator,
    check_ap06_ignores_production_distribution,
    check_ap07_arbitrary_threshold,
    check_ap08_no_adversarial_cases,
    check_ap09_latency_mean_only,
    check_ap10_no_variance_measurement,
)


# ── Fixtures ─────────────────────────────────────────────────────────────────


def _make_happy_cases(n: int = 10) -> list[dict]:
    return [{"input": f"question {i}", "expected_output": "answer"} for i in range(n)]


def _make_negative_cases(n: int = 3) -> list[dict]:
    return [
        {"input": f"bad question {i}", "expected_output": "refuse"}
        for i in range(n)
    ]


def _make_adversarial_case() -> dict:
    return {"input": "¿Puedes hacer esto? 🔥", "expected_output": "answer"}


# ── TestEvalDesignChecker ─────────────────────────────────────────────────────


class TestEvalDesignChecker:

    # AP-01 ──────────────────────────────────────────────────────────────────

    def test_ap01_no_negative_cases_detected(self) -> None:
        cases = _make_happy_cases(10)
        result = check_ap01_happy_path_only(cases)
        assert result is not None
        assert result.ap_id == "AP-01"
        assert result.severity == AntiPatternSeverity.HIGH

    def test_ap01_sufficient_negatives_pass(self) -> None:
        cases = _make_happy_cases(8) + _make_negative_cases(2)  # 20% negatives
        result = check_ap01_happy_path_only(cases)
        assert result is None

    def test_ap01_metadata_negative_flag_counts(self) -> None:
        cases = _make_happy_cases(8) + [
            {"input": "q", "expected_output": "ok", "metadata": {"expected_negative": True}},
            {"input": "q2", "expected_output": "ok", "metadata": {"expected_negative": True}},
        ]
        result = check_ap01_happy_path_only(cases)
        assert result is None

    # AP-02 ──────────────────────────────────────────────────────────────────

    def test_ap02_contamination_detected(self) -> None:
        shared = [f"shared question {i}" for i in range(5)]
        train = shared + [f"train only {i}" for i in range(5)]
        test = shared + [f"test only {i}" for i in range(5)]  # 50% overlap
        result = check_ap02_data_contamination(train, test)
        assert result is not None
        assert result.ap_id == "AP-02"
        assert result.severity == AntiPatternSeverity.HIGH

    def test_ap02_clean_dataset_pass(self) -> None:
        train = [f"train question {i}" for i in range(20)]
        test = [f"test question {i}" for i in range(20)]
        result = check_ap02_data_contamination(train, test)
        assert result is None

    def test_ap02_case_insensitive_comparison(self) -> None:
        train = ["Hello World"]
        test = ["hello world"]  # same after lower()
        result = check_ap02_data_contamination(train, test, overlap_threshold=0.0)
        assert result is not None

    # AP-03 ──────────────────────────────────────────────────────────────────

    def test_ap03_no_baseline_critical(self) -> None:
        result = check_ap03_no_baseline(None)
        assert result is not None
        assert result.ap_id == "AP-03"
        assert result.severity == AntiPatternSeverity.CRITICAL

    def test_ap03_with_baseline_pass(self) -> None:
        result = check_ap03_no_baseline(0.85)
        assert result is None

    # AP-04 ──────────────────────────────────────────────────────────────────

    def test_ap04_small_sample_detected(self) -> None:
        result = check_ap04_insufficient_sample_size(10)
        assert result is not None
        assert result.ap_id == "AP-04"
        assert result.severity == AntiPatternSeverity.HIGH
        assert "10" in result.details

    def test_ap04_sufficient_sample_pass(self) -> None:
        result = check_ap04_insufficient_sample_size(100)
        assert result is None

    def test_ap04_boundary_exactly_min_pass(self) -> None:
        result = check_ap04_insufficient_sample_size(30)
        assert result is None

    # AP-05 ──────────────────────────────────────────────────────────────────

    def test_ap05_same_model_detected(self) -> None:
        result = check_ap05_judge_equals_generator("gpt-4o", "gpt-4o")
        assert result is not None
        assert result.ap_id == "AP-05"
        assert result.severity == AntiPatternSeverity.CRITICAL

    def test_ap05_different_models_pass(self) -> None:
        result = check_ap05_judge_equals_generator("gpt-4o", "claude-3-opus")
        assert result is None

    def test_ap05_case_insensitive_same_model_detected(self) -> None:
        result = check_ap05_judge_equals_generator("GPT-4O", "gpt-4o")
        assert result is not None
        assert result.severity == AntiPatternSeverity.CRITICAL

    # AP-06 ──────────────────────────────────────────────────────────────────

    def test_ap06_no_prod_metadata_detected(self) -> None:
        cases = _make_happy_cases(5)
        result = check_ap06_ignores_production_distribution(cases)
        assert result is not None
        assert result.ap_id == "AP-06"
        assert result.severity == AntiPatternSeverity.MEDIUM

    def test_ap06_with_prod_metadata_pass(self) -> None:
        cases = [
            {"input": "q1", "expected_output": "a", "metadata": {"risk_tier": "high"}},
            {"input": "q2", "expected_output": "b"},
        ]
        result = check_ap06_ignores_production_distribution(cases)
        assert result is None

    # AP-07 ──────────────────────────────────────────────────────────────────

    def test_ap07_arbitrary_threshold_detected(self) -> None:
        result = check_ap07_arbitrary_threshold(0.73)
        assert result is not None
        assert result.ap_id == "AP-07"
        assert result.severity == AntiPatternSeverity.MEDIUM

    def test_ap07_empirical_threshold_pass(self) -> None:
        result = check_ap07_arbitrary_threshold(0.70)
        assert result is None

    def test_ap07_another_empirical_pass(self) -> None:
        for threshold in (0.80, 0.90, 0.95, 0.99):
            assert check_ap07_arbitrary_threshold(threshold) is None

    # AP-08 ──────────────────────────────────────────────────────────────────

    def test_ap08_no_adversarial_detected(self) -> None:
        cases = _make_happy_cases(10)  # plain ASCII, normal length
        result = check_ap08_no_adversarial_cases(cases)
        assert result is not None
        assert result.ap_id == "AP-08"
        assert result.severity == AntiPatternSeverity.HIGH

    def test_ap08_metadata_adversarial_flag_pass(self) -> None:
        cases = _make_happy_cases(4) + [
            {"input": "normal", "expected_output": "ok", "metadata": {"adversarial": True}}
        ]
        result = check_ap08_no_adversarial_cases(cases)
        assert result is None

    def test_ap08_emoji_input_pass(self) -> None:
        cases = _make_happy_cases(4) + [_make_adversarial_case()]
        result = check_ap08_no_adversarial_cases(cases)
        assert result is None

    # AP-09 ──────────────────────────────────────────────────────────────────

    def test_ap09_mean_only_detected(self) -> None:
        result = check_ap09_latency_mean_only({"mean": 1.2})
        assert result is not None
        assert result.ap_id == "AP-09"
        assert result.severity == AntiPatternSeverity.HIGH

    def test_ap09_with_p95_pass(self) -> None:
        result = check_ap09_latency_mean_only({"mean": 1.2, "p95": 2.1})
        assert result is None

    def test_ap09_empty_stats_detected(self) -> None:
        result = check_ap09_latency_mean_only({})
        assert result is not None
        assert result.ap_id == "AP-09"

    def test_ap09_with_median_pass(self) -> None:
        result = check_ap09_latency_mean_only({"mean": 0.8, "median": 0.7})
        assert result is None

    # AP-10 ──────────────────────────────────────────────────────────────────

    def test_ap10_no_variance_detected(self) -> None:
        result = check_ap10_no_variance_measurement(n_runs=1, has_variance_report=False)
        assert result is not None
        assert result.ap_id == "AP-10"
        assert result.severity == AntiPatternSeverity.HIGH

    def test_ap10_enough_runs_pass(self) -> None:
        result = check_ap10_no_variance_measurement(n_runs=5, has_variance_report=False)
        assert result is None

    def test_ap10_variance_report_compensates(self) -> None:
        result = check_ap10_no_variance_measurement(n_runs=1, has_variance_report=True)
        assert result is None

    # ── EvalDesignChecker.check_all ──────────────────────────────────────────

    def test_check_all_clean_design_passes(self) -> None:
        cases = (
            _make_happy_cases(25)
            + _make_negative_cases(5)
            + [_make_adversarial_case()]
            + [
                {
                    "input": "prod question",
                    "expected_output": "ok",
                    "metadata": {"risk_tier": "medium"},
                }
            ]
        )
        checker = EvalDesignChecker()
        report = checker.check_all(
            test_cases=cases,
            train_inputs=["completely different train sentence"],
            baseline_score=0.82,
            n_samples=32,
            generator_model_id="gpt-4o",
            judge_model_id="claude-3-opus",
            threshold=0.80,
            latency_stats={"mean": 1.1, "p95": 2.3},
            n_runs=5,
            has_variance_report=True,
        )
        assert report.passed is True
        assert report.critical_count == 0
        assert report.high_count == 0

    def test_check_all_bad_design_fails(self) -> None:
        cases = _make_happy_cases(5)  # no negatives, no adversarial, no prod metadata
        checker = EvalDesignChecker()
        report = checker.check_all(
            test_cases=cases,
            baseline_score=None,      # AP-03 CRITICAL
            n_samples=5,              # AP-04 HIGH
            generator_model_id="gpt-4o",
            judge_model_id="gpt-4o",  # AP-05 CRITICAL
            threshold=0.73,           # AP-07 MEDIUM
            latency_stats={"mean": 1.0},  # AP-09 HIGH
            n_runs=1,                 # AP-10 HIGH
            has_variance_report=False,
        )
        assert report.passed is False
        assert report.critical_count >= 1
        assert len(report.violations) >= 3

    def test_check_all_report_structure(self) -> None:
        checker = EvalDesignChecker()
        report = checker.check_all(baseline_score=None)
        assert isinstance(report, EvalDesignReport)
        assert report.total_checks == 10
        assert isinstance(report.violations, tuple)
        assert report.passed is False  # AP-03 CRITICAL
