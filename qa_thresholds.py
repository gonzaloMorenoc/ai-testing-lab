"""Tabla 4.2 del Manual QA AI v13: tabla maestra de umbrales.

Esta es la única fuente de verdad de los gates de calidad usados en el repo.
Cualquier módulo que necesite umbrales debe importarlos de aquí en lugar de
hardcodearlos.

Convención editorial del manual (§4.7):
- Las constantes Python usan ASCII y notación con punto decimal.
- Los nombres de métricas son los canónicos en inglés (faithfulness, etc.).

Referencia: Manual QA AI v13, Tabla 4.2 (Cap. 4 "Por qué QA AI no es QA tradicional").
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class RiskLevel(StrEnum):
    """Nivel de exigencia aplicable según criticidad del dominio.

    Manual v13 §4.3 (Matriz de calibración):
    - MINIMUM:  red line de release. Por debajo no se promociona a producción.
    - TARGET:   gate de PR. El día a día opera contra este nivel.
    - HIGH_RISK: dominios regulados (salud, finanzas, legal). Endurece los gates.
    """

    MINIMUM = "minimum"
    TARGET = "target"
    HIGH_RISK = "high_risk"


@dataclass(frozen=True)
class MetricThreshold:
    """Umbrales de una métrica según los tres niveles de la Tabla 4.2."""

    name: str
    minimum: float
    target: float
    high_risk: float
    direction: str = "higher_is_better"
    detail_section: str = ""

    def cutoff(self, level: RiskLevel) -> float:
        if level == RiskLevel.HIGH_RISK:
            return self.high_risk
        if level == RiskLevel.TARGET:
            return self.target
        return self.minimum

    def gate(self, score: float, level: RiskLevel = RiskLevel.TARGET) -> bool:
        cutoff = self.cutoff(level)
        if self.direction == "lower_is_better":
            return score <= cutoff
        return score >= cutoff

    def tier(self, score: float) -> str:
        if self.direction == "lower_is_better":
            if score <= self.high_risk:
                return "pass_high_risk"
            if score <= self.target:
                return "pass_target"
            if score <= self.minimum:
                return "pass_minimum"
            return "fail"
        if score >= self.high_risk:
            return "pass_high_risk"
        if score >= self.target:
            return "pass_target"
        if score >= self.minimum:
            return "pass_minimum"
        return "fail"


# Tabla 4.2 — Manual QA AI v13. Las 10 filas canónicas que el resto del manual referencia.
QA_THRESHOLDS: dict[str, MetricThreshold] = {
    "faithfulness": MetricThreshold(
        "faithfulness", minimum=0.70, target=0.85, high_risk=0.90, detail_section="§7.4"
    ),
    "answer_relevancy": MetricThreshold(
        "answer_relevancy", minimum=0.75, target=0.90, high_risk=0.92, detail_section="§7.4"
    ),
    "context_recall": MetricThreshold(
        "context_recall", minimum=0.70, target=0.85, high_risk=0.90, detail_section="§7.4"
    ),
    "answer_correctness": MetricThreshold(
        "answer_correctness", minimum=0.65, target=0.80, high_risk=0.88, detail_section="§7.4"
    ),
    "refusal_rate": MetricThreshold(
        "refusal_rate", minimum=0.95, target=0.98, high_risk=0.99, detail_section="§25.4"
    ),
    "false_refusal_rate": MetricThreshold(
        "false_refusal_rate",
        minimum=0.05,
        target=0.03,
        high_risk=0.02,
        direction="lower_is_better",
        detail_section="§25.4",
    ),
    "delta_faithfulness_pr": MetricThreshold(
        "delta_faithfulness_pr",
        minimum=-0.03,
        target=-0.01,
        high_risk=-0.005,
        detail_section="§18, §24",
    ),
    "delta_refusal_rate_pr": MetricThreshold(
        "delta_refusal_rate_pr",
        minimum=-0.02,
        target=-0.01,
        high_risk=-0.005,
        detail_section="§24.3",
    ),
    "p95_latency_seconds": MetricThreshold(
        "p95_latency_seconds",
        minimum=2.0,
        target=1.0,
        high_risk=0.5,
        direction="lower_is_better",
        detail_section="§27.2",
    ),
    "cost_per_query_delta_pct": MetricThreshold(
        "cost_per_query_delta_pct",
        minimum=20.0,
        target=10.0,
        high_risk=5.0,
        direction="lower_is_better",
        detail_section="§27.3",
    ),
}


# Aliases para reducir errores de tipeo en imports externos.
THRESHOLDS = QA_THRESHOLDS


@dataclass
class GateResult:
    metric: str
    score: float
    passed: bool
    tier: str
    level: RiskLevel


def evaluate_gates(
    scores: dict[str, float], level: RiskLevel = RiskLevel.TARGET
) -> list[GateResult]:
    """Evalúa un conjunto de métricas contra la Tabla 4.2.

    Métricas no registradas en la tabla se ignoran silenciosamente.
    """
    results: list[GateResult] = []
    for metric, score in scores.items():
        threshold = QA_THRESHOLDS.get(metric)
        if threshold is None:
            continue
        results.append(
            GateResult(
                metric=metric,
                score=score,
                passed=threshold.gate(score, level),
                tier=threshold.tier(score),
                level=level,
            )
        )
    return results


def all_gates_pass(scores: dict[str, float], level: RiskLevel = RiskLevel.TARGET) -> bool:
    """True si todas las métricas registradas superan su gate."""
    return all(r.passed for r in evaluate_gates(scores, level))
