"""Tabla 27.2 del Manual v13: umbrales de regresión de coste por tipo de cambio.

Un PR no debe aumentar el coste medio por query más allá del umbral según el
tipo de cambio. Los porcentajes se expresan como decimales (10 % = 0.10).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from cost_metrics import CostLatencyReport


class ChangeType(StrEnum):
    PROMPT_LONGER = "prompt_longer"
    MODEL_MORE_EXPENSIVE = "model_more_expensive"
    TOP_K_LARGER = "top_k_larger"
    AGENT_MORE_LOOPS = "agent_more_loops"


# Tabla 27.2 — umbrales de Δ permitido por tipo de cambio.
DELTA_THRESHOLDS: dict[ChangeType, float] = {
    ChangeType.PROMPT_LONGER: 0.15,
    ChangeType.MODEL_MORE_EXPENSIVE: 0.20,
    ChangeType.TOP_K_LARGER: 0.25,
    ChangeType.AGENT_MORE_LOOPS: 0.30,
}


@dataclass(frozen=True)
class RegressionViolation:
    metric: str
    baseline: float
    candidate: float
    delta_pct: float
    threshold_pct: float


@dataclass(frozen=True)
class RegressionResult:
    change_type: ChangeType
    passed: bool
    violations: tuple[RegressionViolation, ...] = field(default_factory=tuple)


def _delta_pct(baseline: float, candidate: float) -> float:
    if baseline == 0:
        return float("inf") if candidate > 0 else 0.0
    return (candidate - baseline) / baseline


def _metrics_to_check(change_type: ChangeType) -> tuple[str, ...]:
    if change_type == ChangeType.PROMPT_LONGER:
        return ("tokens_in_mean",)
    if change_type == ChangeType.MODEL_MORE_EXPENSIVE:
        return ("cost_usd_mean",)
    if change_type == ChangeType.TOP_K_LARGER:
        return ("tokens_in_mean",)
    if change_type == ChangeType.AGENT_MORE_LOOPS:
        return ("tool_fan_out_mean", "cost_usd_mean")
    return ()


class CostRegressionChecker:
    """Compara baseline vs candidate según el tipo de cambio."""

    def __init__(self, thresholds: dict[ChangeType, float] | None = None) -> None:
        self.thresholds = thresholds if thresholds is not None else dict(DELTA_THRESHOLDS)

    def check(
        self,
        baseline: CostLatencyReport,
        candidate: CostLatencyReport,
        change_type: ChangeType,
    ) -> RegressionResult:
        max_delta = self.thresholds[change_type]
        violations: list[RegressionViolation] = []
        for metric_name in _metrics_to_check(change_type):
            b = getattr(baseline, metric_name)
            c = getattr(candidate, metric_name)
            delta = _delta_pct(b, c)
            if delta > max_delta:
                violations.append(
                    RegressionViolation(
                        metric=metric_name,
                        baseline=b,
                        candidate=c,
                        delta_pct=delta,
                        threshold_pct=max_delta,
                    )
                )
        return RegressionResult(
            change_type=change_type,
            passed=len(violations) == 0,
            violations=tuple(violations),
        )
