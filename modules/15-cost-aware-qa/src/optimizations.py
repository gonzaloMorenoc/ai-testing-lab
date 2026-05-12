"""Helpers para las 5 optimizaciones del §27.5 del Manual v13."""

from __future__ import annotations

from dataclasses import dataclass

from cost_metrics import QueryRecord


def prompt_cache_hit_rate(records: list[QueryRecord], cached_threshold_tokens: int = 100) -> float:
    """Estima cache hit rate por proxy: queries con tokens_in altos pero coste bajo.

    En proveedores con prompt caching nativo (Anthropic, OpenAI), los inputs
    cacheados se facturan a una tarifa reducida. Si el ratio cost/tokens cae
    por debajo del baseline, se asume cache hit.
    """
    if not records:
        return 0.0
    eligible = [r for r in records if r.tokens_in >= cached_threshold_tokens]
    if not eligible:
        return 0.0
    # Proxy determinista: cost_usd / tokens_in muy bajo ⇒ cache hit
    baseline_ratio = sum(r.cost_usd / max(r.tokens_in, 1) for r in eligible) / len(eligible)
    hits = sum(1 for r in eligible if (r.cost_usd / max(r.tokens_in, 1)) < 0.7 * baseline_ratio)
    return hits / len(eligible)


@dataclass(frozen=True)
class RoutingDecision:
    routed_to_cheap: int
    routed_to_expensive: int
    estimated_savings_usd: float


def simulate_model_routing(
    records: list[QueryRecord],
    simple_threshold_tokens: int = 200,
    cheap_savings_factor: float = 0.85,
) -> RoutingDecision:
    """Simula model routing: queries simples van a un modelo barato.

    cheap_savings_factor = 0.85 ⇒ el modelo barato cuesta 15 % del caro.
    Para tokens_in <= simple_threshold, se asume routing al modelo barato.
    """
    cheap = sum(1 for r in records if r.tokens_in <= simple_threshold_tokens)
    expensive = len(records) - cheap
    savings = sum(r.cost_usd * cheap_savings_factor for r in records if r.tokens_in <= simple_threshold_tokens)
    return RoutingDecision(cheap, expensive, savings)


def context_compression_ratio(original_tokens: int, compressed_tokens: int) -> float:
    """Ratio de compresión = (orig - comp) / orig. 0.0 = sin compresión, 1.0 = todo eliminado."""
    if original_tokens <= 0:
        return 0.0
    if compressed_tokens > original_tokens:
        raise ValueError(
            f"compressed_tokens ({compressed_tokens}) no puede exceder original ({original_tokens})"
        )
    return (original_tokens - compressed_tokens) / original_tokens


def streaming_perceived_latency(ttft_ms: float, total_ms: float) -> float:
    """UX percibida en streaming: latencia hasta primer token.

    El manual §27.5 marca que streaming no reduce coste real pero mejora UX
    porque el usuario percibe el TTFT, no el total. Devuelve el ratio
    percibido/total: 1.0 = no streaming (espera total); cercano a 0 = buena UX.
    """
    if total_ms <= 0:
        return 1.0
    return min(ttft_ms / total_ms, 1.0)


def batching_efficiency(
    batch_size: int, single_query_overhead_ms: float, batched_overhead_ms: float
) -> float:
    """Eficiencia del batching: overhead ahorrado por agrupar N queries.

    Devuelve fracción de overhead ahorrado por query (0..1).
    """
    if batch_size <= 0:
        raise ValueError("batch_size debe ser > 0")
    if batch_size == 1:
        return 0.0
    total_single = batch_size * single_query_overhead_ms
    if total_single <= 0:
        return 0.0
    saved = total_single - batched_overhead_ms
    return max(saved / total_single, 0.0)
