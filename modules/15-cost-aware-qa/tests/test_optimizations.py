"""Tests de optimizations.py — §27.5 del manual."""

import pytest

from cost_metrics import QueryRecord
from optimizations import (
    batching_efficiency,
    context_compression_ratio,
    prompt_cache_hit_rate,
    simulate_model_routing,
    streaming_perceived_latency,
)


class TestPromptCacheHitRate:
    def test_empty_records(self):
        assert prompt_cache_hit_rate([]) == 0.0

    def test_no_eligible_records_below_threshold(self):
        records = [QueryRecord("gpt-4o", 50, 20, 500, cost_usd=0.001)]
        # 50 tokens < 100 threshold ⇒ ningún elegible
        assert prompt_cache_hit_rate(records, cached_threshold_tokens=100) == 0.0

    def test_detects_cache_hits_by_low_ratio(self):
        # 5 queries con ratio normal, 5 con ratio bajo (cache hit)
        records = (
            [QueryRecord("gpt-4o", 1000, 100, 800, cost_usd=0.01)] * 5
            + [QueryRecord("gpt-4o", 1000, 100, 800, cost_usd=0.001)] * 5
        )
        rate = prompt_cache_hit_rate(records, cached_threshold_tokens=100)
        assert rate > 0.0


class TestSimulateModelRouting:
    def test_routes_simple_queries_to_cheap(self):
        records = [
            QueryRecord("gpt-4o", 100, 50, 500, cost_usd=0.01),
            QueryRecord("gpt-4o", 100, 50, 500, cost_usd=0.01),
            QueryRecord("gpt-4o", 500, 200, 1000, cost_usd=0.05),
        ]
        decision = simulate_model_routing(records, simple_threshold_tokens=200)
        assert decision.routed_to_cheap == 2
        assert decision.routed_to_expensive == 1
        assert decision.estimated_savings_usd > 0


class TestContextCompressionRatio:
    def test_no_compression_returns_zero(self):
        assert context_compression_ratio(1000, 1000) == 0.0

    def test_half_compression(self):
        assert context_compression_ratio(1000, 500) == pytest.approx(0.5)

    def test_full_compression(self):
        assert context_compression_ratio(1000, 0) == 1.0

    def test_compressed_greater_than_original_raises(self):
        with pytest.raises(ValueError):
            context_compression_ratio(100, 200)

    def test_zero_original_returns_zero(self):
        assert context_compression_ratio(0, 0) == 0.0


class TestStreamingPerceivedLatency:
    def test_ttft_equals_total_is_one(self):
        assert streaming_perceived_latency(1000, 1000) == 1.0

    def test_fast_ttft_low_ratio(self):
        # TTFT 100 ms de un total de 2 s ⇒ excelente UX (5 %)
        assert streaming_perceived_latency(100, 2000) == pytest.approx(0.05)

    def test_zero_total_returns_one(self):
        assert streaming_perceived_latency(0, 0) == 1.0


class TestBatchingEfficiency:
    def test_batch_of_one_returns_zero(self):
        assert batching_efficiency(1, 100, 100) == 0.0

    def test_batch_saves_overhead(self):
        # 10 queries × 100 ms = 1000 ms single. Batched: 200 ms. Ahorro 80 %.
        eff = batching_efficiency(10, single_query_overhead_ms=100, batched_overhead_ms=200)
        assert eff == pytest.approx(0.8)

    def test_batch_size_zero_raises(self):
        with pytest.raises(ValueError):
            batching_efficiency(0, 100, 100)

    def test_negative_savings_returns_zero(self):
        # Batched más caro que single ⇒ 0 (no negativo)
        assert batching_efficiency(5, single_query_overhead_ms=10, batched_overhead_ms=1000) == 0.0
