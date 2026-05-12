"""Tests de cost_metrics.py."""

import pytest

from cost_metrics import (
    QueryRecord,
    _percentile,
    compute_cost_latency_metrics,
)


class TestPercentile:
    def test_empty_returns_zero(self):
        assert _percentile([], 50) == 0.0

    def test_single_value(self):
        assert _percentile([42.0], 50) == 42.0
        assert _percentile([42.0], 99) == 42.0

    def test_p50_is_median_for_odd_n(self):
        assert _percentile([1, 2, 3, 4, 5], 50) == 3.0

    def test_p95_above_most_values(self):
        values = list(range(100))
        p95 = _percentile(values, 95)
        assert p95 >= 94 and p95 <= 95

    def test_monotonic_in_p(self):
        values = list(range(10))
        assert _percentile(values, 50) <= _percentile(values, 90)


class TestComputeCostLatencyMetrics:
    def test_empty_records_returns_zero_report(self):
        r = compute_cost_latency_metrics([])
        assert r.n_queries == 0
        assert r.cost_usd_mean == 0.0

    def test_n_queries(self, baseline_records):
        r = compute_cost_latency_metrics(baseline_records)
        assert r.n_queries == 10

    def test_mean_tokens(self, baseline_records):
        r = compute_cost_latency_metrics(baseline_records)
        expected_in = sum(b.tokens_in for b in baseline_records) / 10
        assert r.tokens_in_mean == pytest.approx(expected_in)

    def test_p95_lower_than_max(self, baseline_records):
        r = compute_cost_latency_metrics(baseline_records)
        max_lat = max(b.latency_ms_total for b in baseline_records)
        assert r.latency_p95_ms <= max_lat

    def test_p99_greater_or_equal_to_p95(self, baseline_records):
        r = compute_cost_latency_metrics(baseline_records)
        assert r.latency_p99_ms >= r.latency_p95_ms

    def test_retry_rate(self, baseline_records):
        r = compute_cost_latency_metrics(baseline_records)
        # 1 de 10 reintentado
        assert r.retry_rate == pytest.approx(0.1)

    def test_tool_fan_out_mean(self, baseline_records):
        r = compute_cost_latency_metrics(baseline_records)
        expected = sum(b.tool_calls for b in baseline_records) / 10
        assert r.tool_fan_out_mean == pytest.approx(expected)

    def test_ttft_p95_present_when_records_have_ttft(self, baseline_records):
        r = compute_cost_latency_metrics(baseline_records)
        assert r.ttft_p95_ms is not None

    def test_ttft_none_when_no_records_have_ttft(self):
        records = [
            QueryRecord("gpt-4o", 100, 50, 500, time_to_first_token_ms=None),
        ]
        r = compute_cost_latency_metrics(records)
        assert r.ttft_p95_ms is None

    def test_query_record_is_frozen(self):
        r = QueryRecord("gpt-4o", 100, 50, 500)
        with pytest.raises(Exception):
            r.model = "otro"  # type: ignore[misc]
