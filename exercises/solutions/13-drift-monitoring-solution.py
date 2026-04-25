"""
Solución módulo 13: DriftReport con PSI + reglas + timestamp.
"""
from __future__ import annotations

import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "modules" / "13-drift-monitoring"))

from src.alert_rules import AlertResult, mean_drop_alert, p95_alert, psi_alert
from src.drift_detector import compute_psi


@dataclass
class DriftReport:
    psi: float
    alerts: list[AlertResult]
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    @property
    def any_triggered(self) -> bool:
        return any(a.triggered for a in self.alerts)

    def as_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "psi": self.psi,
            "any_triggered": self.any_triggered,
            "alerts": [
                {
                    "rule": a.rule_name,
                    "triggered": a.triggered,
                    "observed": a.observed_value,
                    "message": a.message,
                }
                for a in self.alerts
            ],
        }


def run_drift_analysis(
    reference: list[float],
    current: list[float],
    rules: list[Callable],
) -> DriftReport:
    psi = compute_psi(reference, current)
    psi_result = psi_alert(threshold=0.2)(psi)
    score_alerts = [rule(current) for rule in rules]
    return DriftReport(psi=psi, alerts=[psi_result, *score_alerts])


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    ref = rng.normal(0.8, 0.05, 200).tolist()
    cur = rng.normal(0.5, 0.1, 200).tolist()

    ref_mean = float(np.mean(ref))
    report = run_drift_analysis(
        reference=ref,
        current=cur,
        rules=[
            mean_drop_alert(reference_mean=ref_mean, threshold_pct=0.1),
            p95_alert(limit=0.9),
        ],
    )
    import json
    print(json.dumps(report.as_dict(), indent=2))
