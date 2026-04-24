from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable

import numpy as np


@dataclass
class AlertResult:
    triggered: bool
    rule_name: str
    observed_value: float
    threshold: float
    message: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def psi_alert(threshold: float = 0.2) -> Callable[[float], AlertResult]:
    def check(psi: float) -> AlertResult:
        triggered = psi > threshold
        return AlertResult(
            triggered=triggered,
            rule_name="psi_alert",
            observed_value=psi,
            threshold=threshold,
            message=f"PSI={psi:.4f} {'>' if triggered else '<='} {threshold}",
        )
    return check


def mean_drop_alert(
    reference_mean: float,
    threshold_pct: float = 0.1,
) -> Callable[[list[float]], AlertResult]:
    """Alert when the current mean drops more than threshold_pct below reference_mean.

    Args:
        reference_mean: Expected mean from baseline period. Must be > 0.
        threshold_pct: Fractional drop to trigger alert (default 0.1 = 10%).

    Note: Designed for positive metrics (scores, relevance, quality). If
    reference_mean <= 0 the drop percentage is undefined and no alert fires.
    """
    def check(current: list[float]) -> AlertResult:
        cur_mean = float(np.mean(current))
        drop_pct = (reference_mean - cur_mean) / reference_mean if reference_mean != 0 else 0.0
        triggered = drop_pct > threshold_pct
        return AlertResult(
            triggered=triggered,
            rule_name="mean_drop_alert",
            observed_value=cur_mean,
            threshold=reference_mean * (1.0 - threshold_pct),
            message=f"mean dropped {drop_pct:.1%} ({'ALERT' if triggered else 'ok'})",
        )
    return check


def p95_alert(limit: float) -> Callable[[list[float]], AlertResult]:
    def check(current: list[float]) -> AlertResult:
        p95 = float(np.percentile(current, 95))
        triggered = p95 > limit
        return AlertResult(
            triggered=triggered,
            rule_name="p95_alert",
            observed_value=p95,
            threshold=limit,
            message=f"p95={p95:.4f} {'>' if triggered else '<='} {limit}",
        )
    return check


def evaluate_rules(
    rules: list[Callable],
    data: list[float],
) -> list[AlertResult]:
    """Apply a list of score-level rules to data.

    Each rule must be a callable that accepts list[float] and returns AlertResult.
    Use mean_drop_alert and p95_alert here. Note: psi_alert accepts a float (PSI
    value), not a list — invoke it separately: psi_alert(threshold)(compute_psi(...)).
    """
    return [rule(data) for rule in rules]
