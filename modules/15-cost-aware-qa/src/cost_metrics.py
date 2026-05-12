"""Tabla 27.1 del Manual v13: 7 métricas de coste y latencia.

Cada record es una observación de una query en producción o en eval. El
agregador devuelve una `CostLatencyReport` con percentiles y umbrales.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QueryRecord:
    """Observación de una query en runtime o eval."""

    model: str
    tokens_in: int
    tokens_out: int
    latency_ms_total: float
    time_to_first_token_ms: float | None = None
    tool_calls: int = 0
    retried: bool = False
    cost_usd: float = 0.0


@dataclass(frozen=True)
class CostLatencyReport:
    """Agregación de Tabla 27.1 sobre una ventana de queries."""

    n_queries: int
    tokens_in_mean: float
    tokens_out_mean: float
    cost_usd_mean: float
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    ttft_p95_ms: float | None
    tool_fan_out_mean: float
    retry_rate: float


def _percentile(values: list[float], p: float) -> float:
    """Percentil p (0..100) por interpolación lineal. Determinista, sin numpy."""
    if not values:
        return 0.0
    s = sorted(values)
    if len(s) == 1:
        return s[0]
    rank = (p / 100) * (len(s) - 1)
    lo = int(rank)
    hi = min(lo + 1, len(s) - 1)
    frac = rank - lo
    return s[lo] + (s[hi] - s[lo]) * frac


def compute_cost_latency_metrics(records: list[QueryRecord]) -> CostLatencyReport:
    if not records:
        return CostLatencyReport(
            n_queries=0,
            tokens_in_mean=0.0,
            tokens_out_mean=0.0,
            cost_usd_mean=0.0,
            latency_p50_ms=0.0,
            latency_p95_ms=0.0,
            latency_p99_ms=0.0,
            ttft_p95_ms=None,
            tool_fan_out_mean=0.0,
            retry_rate=0.0,
        )
    n = len(records)
    latencies = [r.latency_ms_total for r in records]
    ttfts = [r.time_to_first_token_ms for r in records if r.time_to_first_token_ms is not None]
    return CostLatencyReport(
        n_queries=n,
        tokens_in_mean=sum(r.tokens_in for r in records) / n,
        tokens_out_mean=sum(r.tokens_out for r in records) / n,
        cost_usd_mean=sum(r.cost_usd for r in records) / n,
        latency_p50_ms=_percentile(latencies, 50),
        latency_p95_ms=_percentile(latencies, 95),
        latency_p99_ms=_percentile(latencies, 99),
        ttft_p95_ms=_percentile(ttfts, 95) if ttfts else None,
        tool_fan_out_mean=sum(r.tool_calls for r in records) / n,
        retry_rate=sum(1 for r in records if r.retried) / n,
    )
