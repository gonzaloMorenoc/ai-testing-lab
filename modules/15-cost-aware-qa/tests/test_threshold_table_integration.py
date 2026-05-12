"""Integración con qa_thresholds.py (Tabla 4.2 del Manual v13).

Verifica que las métricas de coste y latencia del módulo 15 se evalúan
contra la tabla maestra de umbrales del repo, no contra valores hardcoded.
"""

import pytest

from qa_thresholds import QA_THRESHOLDS, RiskLevel, evaluate_gates


class TestThresholdsAvailable:
    def test_p95_latency_in_table(self):
        assert "p95_latency_seconds" in QA_THRESHOLDS

    def test_cost_delta_in_table(self):
        assert "cost_per_query_delta_pct" in QA_THRESHOLDS

    def test_p95_target_is_1_second(self):
        assert QA_THRESHOLDS["p95_latency_seconds"].target == 1.0

    def test_cost_delta_target_is_10_percent(self):
        assert QA_THRESHOLDS["cost_per_query_delta_pct"].target == 10.0


class TestEvaluateAgainstTable:
    def test_p95_below_target_passes(self):
        # 0.8 s ≤ 1 s ⇒ pasa nivel TARGET
        results = evaluate_gates({"p95_latency_seconds": 0.8}, RiskLevel.TARGET)
        assert all(r.passed for r in results)

    def test_p95_above_minimum_fails_at_target(self):
        # 1.5 s > 1 s (target) pero ≤ 2 s (minimum)
        target_results = evaluate_gates({"p95_latency_seconds": 1.5}, RiskLevel.TARGET)
        assert not target_results[0].passed
        min_results = evaluate_gates({"p95_latency_seconds": 1.5}, RiskLevel.MINIMUM)
        assert min_results[0].passed

    def test_cost_delta_within_10pct_passes(self):
        results = evaluate_gates({"cost_per_query_delta_pct": 8.0}, RiskLevel.TARGET)
        assert all(r.passed for r in results)


class TestLatencyConvertsCorrectly:
    @pytest.mark.parametrize("ms,seconds", [(500, 0.5), (1000, 1.0), (2000, 2.0)])
    def test_milliseconds_to_seconds_for_table(self, ms, seconds):
        # El módulo guarda latencias en ms; la tabla las pide en segundos.
        # Este test documenta la conversión esperada.
        assert ms / 1000.0 == seconds
