from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RiskLevel(str, Enum):
    STANDARD = "standard"
    HIGH_RISK = "high_risk"


@dataclass(frozen=True)
class MetricThreshold:
    """Umbrales de una métrica según Tabla 1.2 del Manual QA AI v12."""
    name: str
    minimum: float
    target: float
    high_risk: float

    def gate(self, score: float, level: RiskLevel = RiskLevel.STANDARD) -> bool:
        """True si el score supera el gate para el nivel dado."""
        cutoff = self.high_risk if level == RiskLevel.HIGH_RISK else self.minimum
        return score >= cutoff

    def tier(self, score: float) -> str:
        """Clasifica el score en 'pass_high_risk', 'pass_target', 'pass_minimum' o 'fail'."""
        if score >= self.high_risk:
            return "pass_high_risk"
        if score >= self.target:
            return "pass_target"
        if score >= self.minimum:
            return "pass_minimum"
        return "fail"


# Tabla 1.2 — Umbrales maestros del Manual QA AI v12
QA_THRESHOLDS: dict[str, MetricThreshold] = {
    "faithfulness": MetricThreshold("faithfulness", minimum=0.70, target=0.85, high_risk=0.90),
    "answer_relevancy": MetricThreshold("answer_relevancy", minimum=0.75, target=0.90, high_risk=0.92),
    "context_recall": MetricThreshold("context_recall", minimum=0.70, target=0.85, high_risk=0.90),
    "answer_correctness": MetricThreshold("answer_correctness", minimum=0.65, target=0.80, high_risk=0.88),
    "refusal_rate": MetricThreshold("refusal_rate", minimum=0.95, target=0.98, high_risk=0.99),
}


@dataclass
class GateResult:
    metric: str
    score: float
    passed: bool
    tier: str
    level: RiskLevel


class QAGateChecker:
    """Evalúa si un conjunto de métricas supera los quality gates de CI/CD."""

    def __init__(self, level: RiskLevel = RiskLevel.STANDARD) -> None:
        self.level = level

    def check(self, scores: dict[str, float]) -> list[GateResult]:
        results = []
        for metric, score in scores.items():
            threshold = QA_THRESHOLDS.get(metric)
            if threshold is None:
                continue
            results.append(GateResult(
                metric=metric,
                score=score,
                passed=threshold.gate(score, self.level),
                tier=threshold.tier(score),
                level=self.level,
            ))
        return results

    def all_passed(self, scores: dict[str, float]) -> bool:
        return all(r.passed for r in self.check(scores))
