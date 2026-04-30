from __future__ import annotations

import os
from pathlib import Path

import pytest

from src.prompt_registry import PromptRegistry
from src.regression_checker import RegressionChecker, is_significant


class TestPromptRegistry:
    def test_get_prompt_by_version(self, registry: PromptRegistry) -> None:
        v1 = registry.get("support_response", "v1")
        assert "support agent" in v1.template

    def test_get_prompt_v2_has_more_detail(self, registry: PromptRegistry) -> None:
        v2 = registry.get("support_response", "v2")
        assert "concisely" in v2.template or "accurately" in v2.template

    def test_list_versions(self, registry: PromptRegistry) -> None:
        versions = registry.list_versions("support_response")
        assert "v1" in versions
        assert "v2" in versions

    def test_get_latest_returns_v2(self, registry: PromptRegistry) -> None:
        latest = registry.latest("support_response")
        assert latest.version == "v2"

    def test_render_replaces_variables(self, registry: PromptRegistry) -> None:
        v1 = registry.get("support_response", "v1")
        rendered = v1.render(question="What is the return policy?")
        assert "What is the return policy?" in rendered
        assert "{question}" not in rendered

    def test_missing_prompt_raises_key_error(self, registry: PromptRegistry) -> None:
        with pytest.raises(KeyError):
            registry.get("nonexistent", "v1")


class TestRegressionChecker:
    def test_improvement_not_regression(self, checker: RegressionChecker) -> None:
        report = checker.check("support_response", "v1", 0.75, "v2", 0.85)
        print(f"\n  {report.summary()}")
        assert not report.regression_detected
        assert report.delta > 0

    def test_degradation_detected(self, checker: RegressionChecker) -> None:
        report = checker.check("support_response", "v1", 0.85, "v2", 0.70)
        print(f"\n  {report.summary()}")
        assert report.regression_detected
        assert report.delta < 0

    def test_within_tolerance_not_regression(self, checker: RegressionChecker) -> None:
        report = checker.check("support_response", "v1", 0.80, "v2", 0.75)
        print(f"\n  {report.summary()} (delta={report.delta}, threshold={checker.threshold})")
        assert not report.regression_detected

    def test_multiple_metrics_partial_regression(self, checker: RegressionChecker) -> None:
        scores = {
            "relevancy": (0.80, 0.85),
            "faithfulness": (0.90, 0.70),
        }
        reports = checker.check_multiple("support_response", "v1", "v2", scores)
        assert len(reports) == 2
        regressions = [r for r in reports if r.regression_detected]
        assert len(regressions) == 1
        assert regressions[0].metric_name == "faithfulness"

    def test_promptfooconfig_is_valid_yaml(self) -> None:
        import yaml

        config_path = Path(__file__).parent.parent / "promptfooconfig.yaml"
        assert config_path.exists(), "promptfooconfig.yaml debe existir"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert "prompts" in config
        assert "providers" in config
        assert "tests" in config
        assert len(config["prompts"]) >= 2

    def test_summary_format(self, checker: RegressionChecker) -> None:
        report = checker.check("support_response", "v1", 0.85, "v2", 0.70)
        summary = report.summary()
        assert "REGRESSION" in summary
        assert "v1" in summary
        assert "v2" in summary


class TestSignificance:
    def test_large_delta_many_samples_is_significant(self) -> None:
        # Delta of 0.15 with 200 samples is a real signal
        assert is_significant(delta=-0.15, n_samples=200, baseline_score=0.80)

    def test_small_delta_few_samples_not_significant(self) -> None:
        # Delta of 0.03 with 10 samples is noise
        assert not is_significant(delta=-0.03, n_samples=10, baseline_score=0.80)

    def test_same_delta_more_samples_becomes_significant(self) -> None:
        delta, baseline = -0.05, 0.80
        assert not is_significant(delta=delta, n_samples=20, baseline_score=baseline)
        assert is_significant(delta=delta, n_samples=500, baseline_score=baseline)

    def test_zero_samples_always_not_significant(self) -> None:
        assert not is_significant(delta=-0.5, n_samples=0, baseline_score=0.80)

    def test_strict_alpha_harder_to_reach(self) -> None:
        # Delta that passes at 0.05 but not at 0.01
        assert is_significant(delta=-0.10, n_samples=100, baseline_score=0.80, alpha=0.05)
        assert not is_significant(delta=-0.03, n_samples=50, baseline_score=0.80, alpha=0.01)

    @pytest.mark.slow
    def test_with_promptfoo_cli(self) -> None:
        if not os.getenv("GROQ_API_KEY"):
            pytest.skip("GROQ_API_KEY no encontrado")
        import subprocess

        result = subprocess.run(
            ["promptfoo", "eval", "--config", "promptfooconfig.yaml", "--no-cache"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        print(f"\n  Promptfoo output: {result.stdout[-300:]}")
        assert result.returncode == 0, f"Promptfoo falló: {result.stderr}"


class TestEvaluateWithVariance:
    """Tests for Cap 29 §29.4 — evaluate_with_variance pattern."""

    from src.variance_evaluator import (
        REGRESSION_THRESHOLDS,
        compare_pairwise,
        evaluate_with_variance,
    )

    def test_high_scores_above_threshold_passes(self) -> None:
        from src.variance_evaluator import evaluate_with_variance

        report = evaluate_with_variance([0.88, 0.90, 0.86, 0.91, 0.89], 0.85)
        assert report.passed is True
        assert report.median >= 0.85
        assert report.ci95_low >= 0.85 - 0.02
        assert report.n_runs == 5

    def test_low_scores_below_threshold_fails(self) -> None:
        from src.variance_evaluator import evaluate_with_variance

        report = evaluate_with_variance([0.60, 0.62, 0.58, 0.61, 0.59], 0.85)
        assert report.passed is False
        assert report.median < 0.85

    def test_empty_scores_raises_value_error(self) -> None:
        from src.variance_evaluator import evaluate_with_variance

        with pytest.raises(ValueError, match="vacío"):
            evaluate_with_variance([], 0.85)

    def test_report_fields_are_populated(self) -> None:
        from src.variance_evaluator import evaluate_with_variance

        report = evaluate_with_variance([0.88, 0.90, 0.86, 0.91, 0.89], 0.85, metric="faithfulness")
        assert report.metric == "faithfulness"
        assert report.expected_threshold == 0.85
        assert report.ci95_low <= report.median <= report.ci95_high
        assert report.iqr >= 0.0


class TestComparePairwise:
    """Tests for Cap 21 — compare_pairwise pattern."""

    def test_large_faithfulness_drop_is_regression(self) -> None:
        from src.variance_evaluator import compare_pairwise

        report = compare_pairwise({"faithfulness": 0.85}, {"faithfulness": 0.78})
        assert report.delta["faithfulness"] == pytest.approx(-0.07, abs=1e-4)
        assert report.regression is True
        assert "faithfulness" in report.failing_metrics

    def test_small_faithfulness_drop_not_regression(self) -> None:
        from src.variance_evaluator import compare_pairwise

        report = compare_pairwise({"faithfulness": 0.85}, {"faithfulness": 0.84})
        assert report.delta["faithfulness"] == pytest.approx(-0.01, abs=1e-4)
        assert report.regression is False
        assert report.failing_metrics == []

    def test_refusal_rate_stricter_threshold_triggers_regression(self) -> None:
        # refusal_rate threshold is -0.02, stricter than the default -0.03.
        # A drop of 0.025 (delta=-0.025) breaches it, whereas the same drop
        # would not trigger a regression for a metric with the default -0.03 threshold.
        from src.variance_evaluator import REGRESSION_THRESHOLDS, compare_pairwise

        assert REGRESSION_THRESHOLDS["refusal_rate"] == -0.02
        report = compare_pairwise({"refusal_rate": 0.980}, {"refusal_rate": 0.955})
        assert report.delta["refusal_rate"] == pytest.approx(-0.025, abs=1e-4)
        assert report.regression is True
        assert "refusal_rate" in report.failing_metrics

    def test_refusal_rate_small_drop_below_strict_threshold_no_regression(self) -> None:
        # delta=-0.01 does not breach the -0.02 refusal_rate threshold
        from src.variance_evaluator import compare_pairwise

        report = compare_pairwise({"refusal_rate": 0.98}, {"refusal_rate": 0.97})
        assert report.delta["refusal_rate"] == pytest.approx(-0.01, abs=1e-4)
        assert report.regression is False

    def test_improvement_is_never_regression(self) -> None:
        from src.variance_evaluator import compare_pairwise

        report = compare_pairwise(
            {"faithfulness": 0.80, "answer_relevancy": 0.75},
            {"faithfulness": 0.90, "answer_relevancy": 0.85},
        )
        assert report.regression is False
        assert all(d > 0 for d in report.delta.values())

    def test_delta_computed_for_all_baseline_keys(self) -> None:
        from src.variance_evaluator import compare_pairwise

        baseline = {"faithfulness": 0.85, "answer_relevancy": 0.80, "consistency": 0.90}
        candidate = {"faithfulness": 0.82, "answer_relevancy": 0.81, "consistency": 0.88}
        report = compare_pairwise(baseline, candidate)
        assert set(report.delta.keys()) == set(baseline.keys())
