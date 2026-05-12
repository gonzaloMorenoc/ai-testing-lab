"""Tests de cost_regression.py — Tabla 27.2 del manual."""

from cost_metrics import CostLatencyReport
from cost_regression import (
    DELTA_THRESHOLDS,
    ChangeType,
    CostRegressionChecker,
)


def _make_report(tokens_in=1000.0, cost=0.001, tool_fan_out=2.0) -> CostLatencyReport:
    return CostLatencyReport(
        n_queries=10,
        tokens_in_mean=tokens_in,
        tokens_out_mean=300.0,
        cost_usd_mean=cost,
        latency_p50_ms=500.0,
        latency_p95_ms=1000.0,
        latency_p99_ms=1500.0,
        ttft_p95_ms=400.0,
        tool_fan_out_mean=tool_fan_out,
        retry_rate=0.01,
    )


class TestPromptLonger:
    def test_within_15pct_passes(self):
        b = _make_report(tokens_in=1000)
        c = _make_report(tokens_in=1100)  # +10 %
        r = CostRegressionChecker().check(b, c, ChangeType.PROMPT_LONGER)
        assert r.passed

    def test_over_15pct_fails(self):
        b = _make_report(tokens_in=1000)
        c = _make_report(tokens_in=1200)  # +20 %
        r = CostRegressionChecker().check(b, c, ChangeType.PROMPT_LONGER)
        assert not r.passed
        assert r.violations[0].metric == "tokens_in_mean"


class TestModelMoreExpensive:
    def test_within_20pct_passes(self):
        b = _make_report(cost=0.001)
        c = _make_report(cost=0.0011)  # +10 %
        r = CostRegressionChecker().check(b, c, ChangeType.MODEL_MORE_EXPENSIVE)
        assert r.passed

    def test_over_20pct_fails(self):
        b = _make_report(cost=0.001)
        c = _make_report(cost=0.0013)  # +30 %
        r = CostRegressionChecker().check(b, c, ChangeType.MODEL_MORE_EXPENSIVE)
        assert not r.passed


class TestTopKLarger:
    def test_within_25pct_passes(self):
        b = _make_report(tokens_in=1000)
        c = _make_report(tokens_in=1200)  # +20 %
        r = CostRegressionChecker().check(b, c, ChangeType.TOP_K_LARGER)
        assert r.passed

    def test_over_25pct_fails(self):
        b = _make_report(tokens_in=1000)
        c = _make_report(tokens_in=1300)  # +30 %
        r = CostRegressionChecker().check(b, c, ChangeType.TOP_K_LARGER)
        assert not r.passed


class TestAgentMoreLoops:
    def test_within_30pct_passes(self):
        b = _make_report(tool_fan_out=2.0, cost=0.001)
        c = _make_report(tool_fan_out=2.5, cost=0.0012)  # +25 % y +20 %
        r = CostRegressionChecker().check(b, c, ChangeType.AGENT_MORE_LOOPS)
        assert r.passed

    def test_two_metrics_both_checked(self):
        b = _make_report(tool_fan_out=2.0, cost=0.001)
        c = _make_report(tool_fan_out=3.0, cost=0.0015)  # +50 % en ambos
        r = CostRegressionChecker().check(b, c, ChangeType.AGENT_MORE_LOOPS)
        assert not r.passed
        # Ambas métricas violan
        assert len(r.violations) == 2


class TestDeltaThresholds:
    def test_all_change_types_have_threshold(self):
        for ct in ChangeType:
            assert ct in DELTA_THRESHOLDS

    def test_zero_baseline_with_positive_candidate_is_inf_delta(self):
        b = _make_report(tokens_in=0)
        c = _make_report(tokens_in=100)
        r = CostRegressionChecker().check(b, c, ChangeType.PROMPT_LONGER)
        assert not r.passed
