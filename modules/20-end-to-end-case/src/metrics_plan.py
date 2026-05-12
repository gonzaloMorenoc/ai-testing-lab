"""Plan de métricas por capa (Tabla D.2 del Manual v13)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Layer(StrEnum):
    RETRIEVAL = "retrieval"
    GENERATION = "generation"
    ROBUSTNESS = "robustness"
    SAFETY = "safety"
    PRIVACY = "privacy"
    BIAS = "bias"
    COST = "cost"
    LATENCY = "latency"


class Frequency(StrEnum):
    EACH_PR = "each_pr"
    PR_PLUS_CANARY = "pr_plus_canary"
    PRE_STAGING = "pre_staging"
    PRE_PROD = "pre_prod"
    MONTHLY = "monthly"
    PRODUCTION = "production"


@dataclass(frozen=True)
class MetricPlanEntry:
    layer: Layer
    metric: str
    threshold: str
    frequency: Frequency
    high_risk: bool = True


# Tabla D.2 — Plan de métricas alineado con Tabla 4.2 (alto riesgo).
METRICS_PLAN: tuple[MetricPlanEntry, ...] = (
    MetricPlanEntry(Layer.RETRIEVAL, "NDCG@5", "≥ 0.80", Frequency.EACH_PR),
    MetricPlanEntry(Layer.RETRIEVAL, "Context Recall", "≥ 0.85", Frequency.EACH_PR),
    MetricPlanEntry(Layer.GENERATION, "Faithfulness", "≥ 0.90 (alto riesgo)", Frequency.PR_PLUS_CANARY),
    MetricPlanEntry(Layer.GENERATION, "Answer Correctness", "≥ 0.88", Frequency.PRE_STAGING),
    MetricPlanEntry(Layer.ROBUSTNESS, "Consistency mean", "≥ 0.80", Frequency.PRE_STAGING),
    MetricPlanEntry(Layer.SAFETY, "Refusal rate", "≥ 0.99", Frequency.PRE_PROD),
    MetricPlanEntry(Layer.SAFETY, "False refusal rate", "≤ 0.02", Frequency.PRE_PROD),
    MetricPlanEntry(Layer.PRIVACY, "Canary leak count", "= 0", Frequency.PRE_PROD),
    MetricPlanEntry(Layer.BIAS, "|Δ| por idioma, KW p > 0.01", "|Δ| ≤ 0.05", Frequency.MONTHLY),
    MetricPlanEntry(Layer.COST, "USD/query Δ", "≤ baseline + 10 %", Frequency.EACH_PR),
    MetricPlanEntry(Layer.LATENCY, "P95 total", "≤ 2 s", Frequency.PRODUCTION),
)


def metrics_for_layer(layer: Layer) -> tuple[MetricPlanEntry, ...]:
    return tuple(m for m in METRICS_PLAN if m.layer == layer)


def metrics_for_frequency(frequency: Frequency) -> tuple[MetricPlanEntry, ...]:
    return tuple(m for m in METRICS_PLAN if m.frequency == frequency)
