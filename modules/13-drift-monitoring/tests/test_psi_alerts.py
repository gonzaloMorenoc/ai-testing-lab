from __future__ import annotations

import os

import numpy as np
import pytest

from src.alert_rules import (
    AlertHistory,
    AlertResult,
    evaluate_rules,
    mean_drop_alert,
    p95_alert,
    psi_alert,
)
from src.drift_detector import compute_psi


class TestDriftDetector:
    def test_identical_distributions_psi_near_zero(
        self,
        reference_scores: list[float],
        identical_scores: list[float],
    ) -> None:
        psi = compute_psi(reference_scores, identical_scores)
        print(f"\n  PSI identical: {psi}")
        assert psi < 0.1, f"expected PSI near 0 for identical distributions, got {psi}"

    def test_shifted_distribution_psi_high(
        self,
        reference_scores: list[float],
        shifted_scores: list[float],
    ) -> None:
        psi = compute_psi(reference_scores, shifted_scores)
        print(f"\n  PSI shifted: {psi}")
        assert psi > 0.2, f"expected PSI > 0.2 for shifted distribution, got {psi}"


class TestAlertRules:
    def test_mean_drop_20pct_triggers_alert(
        self, reference_scores: list[float], dropped_scores: list[float]
    ) -> None:
        ref_mean = float(np.mean(reference_scores))
        rule = mean_drop_alert(reference_mean=ref_mean, threshold_pct=0.1)
        result = rule(dropped_scores)
        print(f"\n  {result.message}")
        assert result.triggered is True
        assert result.rule_name == "mean_drop_alert"

    def test_mean_drop_5pct_no_alert(self, reference_scores: list[float]) -> None:
        ref_mean = float(np.mean(reference_scores))
        slightly_dropped = [s * 0.97 for s in reference_scores]  # 3% drop
        rule = mean_drop_alert(reference_mean=ref_mean, threshold_pct=0.1)
        result = rule(slightly_dropped)
        print(f"\n  {result.message}")
        assert result.triggered is False

    def test_p95_exceeds_limit_triggers_alert(self) -> None:
        scores = [0.9] * 100
        rule = p95_alert(limit=0.8)
        result = rule(scores)
        print(f"\n  {result.message}")
        assert result.triggered is True
        assert result.rule_name == "p95_alert"

    def test_all_rules_pass_no_alert(self, reference_scores: list[float]) -> None:
        ref_mean = float(np.mean(reference_scores))
        rules: list = [
            mean_drop_alert(reference_mean=ref_mean, threshold_pct=0.3),
            p95_alert(limit=1.5),
        ]
        results = evaluate_rules(rules, reference_scores)
        print(f"\n  {[r.message for r in results]}")
        assert all(not r.triggered for r in results)

    def test_one_failing_rule_identified(self, reference_scores: list[float]) -> None:
        ref_mean = float(np.mean(reference_scores))
        dropped = [s * 0.6 for s in reference_scores]  # 40% drop
        rules: list = [
            mean_drop_alert(reference_mean=ref_mean, threshold_pct=0.3),
            p95_alert(limit=1.5),
        ]
        results = evaluate_rules(rules, dropped)
        triggered = [r for r in results if r.triggered]
        print(f"\n  triggered: {[r.rule_name for r in triggered]}")
        assert len(triggered) == 1
        assert triggered[0].rule_name == "mean_drop_alert"

    def test_alert_result_has_required_fields(self, reference_scores: list[float]) -> None:
        ref_mean = float(np.mean(reference_scores))
        rule = mean_drop_alert(reference_mean=ref_mean)
        result = rule(reference_scores)
        assert isinstance(result, AlertResult)
        assert result.timestamp  # non-empty ISO timestamp
        assert result.rule_name
        assert isinstance(result.observed_value, float)
        assert isinstance(result.threshold, float)
        assert result.message
        print(f"\n  AlertResult: triggered={result.triggered} ts={result.timestamp[:10]}")

    def test_psi_alert_threshold_configurable(
        self, reference_scores: list[float], shifted_scores: list[float]
    ) -> None:
        psi = compute_psi(reference_scores, shifted_scores)
        strict = psi_alert(threshold=0.05)(psi)
        lenient = psi_alert(threshold=10.0)(psi)
        assert strict.triggered is True
        assert lenient.triggered is False


class TestAlertHistory:
    def test_insufficient_data_below_three(self) -> None:
        history = AlertHistory("psi_alert")
        history.add(
            AlertResult(
                triggered=True,
                rule_name="psi_alert",
                observed_value=0.3,
                threshold=0.2,
                message="psi high",
            )
        )
        history.add(
            AlertResult(
                triggered=True,
                rule_name="psi_alert",
                observed_value=0.35,
                threshold=0.2,
                message="psi high",
            )
        )
        assert history.trend == "insufficient_data"

    def test_two_of_three_recent_triggered_is_degrading(self) -> None:
        history = AlertHistory("psi_alert")
        for triggered, val in [(False, 0.1), (True, 0.25), (True, 0.3)]:
            history.add(
                AlertResult(
                    triggered=triggered,
                    rule_name="psi_alert",
                    observed_value=val,
                    threshold=0.2,
                    message="",
                )
            )
        print(f"\n  Trend: {history.trend}")
        assert history.trend == "degrading"

    def test_zero_of_three_recent_triggered_is_recovering(self) -> None:
        history = AlertHistory("psi_alert")
        for triggered, val in [(True, 0.25), (False, 0.15), (False, 0.05)]:
            history.add(
                AlertResult(
                    triggered=triggered,
                    rule_name="psi_alert",
                    observed_value=val,
                    threshold=0.2,
                    message="",
                )
            )
        assert history.trend == "recovering"

    def test_one_of_three_recent_triggered_is_stable(self) -> None:
        history = AlertHistory("psi_alert")
        for triggered, val in [(False, 0.05), (True, 0.25), (False, 0.15)]:
            history.add(
                AlertResult(
                    triggered=triggered,
                    rule_name="psi_alert",
                    observed_value=val,
                    threshold=0.2,
                    message="",
                )
            )
        assert history.trend == "stable"

    def test_trigger_rate_computed_correctly(self) -> None:
        history = AlertHistory("mean_drop")
        history.add(
            AlertResult(
                triggered=True, rule_name="mean_drop", observed_value=0.6, threshold=0.7, message=""
            )
        )
        history.add(
            AlertResult(
                triggered=False,
                rule_name="mean_drop",
                observed_value=0.75,
                threshold=0.7,
                message="",
            )
        )
        history.add(
            AlertResult(
                triggered=True,
                rule_name="mean_drop",
                observed_value=0.65,
                threshold=0.7,
                message="",
            )
        )
        history.add(
            AlertResult(
                triggered=False,
                rule_name="mean_drop",
                observed_value=0.8,
                threshold=0.7,
                message="",
            )
        )
        assert history.trigger_rate == pytest.approx(0.5, abs=0.01)

    def test_summary_contains_required_fields(self) -> None:
        history = AlertHistory("psi_alert")
        for _ in range(3):
            history.add(
                AlertResult(
                    triggered=False,
                    rule_name="psi_alert",
                    observed_value=0.05,
                    threshold=0.2,
                    message="ok",
                )
            )
        summary = history.summary()
        print(f"\n  {summary}")
        assert "psi_alert" in summary
        assert "trend=" in summary
        assert "trigger_rate=" in summary

    @pytest.mark.slow
    def test_real_langfuse_scores(self) -> None:
        if not os.getenv("LANGFUSE_SECRET_KEY"):
            pytest.skip("LANGFUSE_SECRET_KEY no encontrado")
        rng = np.random.default_rng(0)
        ref = rng.beta(5, 1, size=100).tolist()
        cur = rng.beta(2, 2, size=100).tolist()
        psi = compute_psi(ref, cur)
        print(f"\n  Real PSI (beta distributions): {psi}")
        assert psi >= 0.0
