from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field

N_RUNS_PR = 5
N_RUNS_NIGHTLY = 15
ACCEPTANCE_MARGIN = 0.02  # banda de aceptación intencional sobre el umbral nominal

# Tabla 21.1 — Umbrales de regresión de prompt
REGRESSION_THRESHOLDS: dict[str, float] = {
    "faithfulness":     -0.03,
    "answer_relevancy": -0.03,
    "refusal_rate":     -0.02,  # más estricto: security review
    "consistency":      -0.03,
}


@dataclass
class VarianceReport:
    """Resultado de evaluate_with_variance (§29.4)."""
    metric: str
    median: float
    ci95_low: float
    ci95_high: float
    iqr: float
    passed: bool  # median >= threshold AND ci_low >= threshold - ACCEPTANCE_MARGIN
    n_runs: int
    expected_threshold: float


@dataclass
class PairwiseRegressionReport:
    baseline_scores: dict[str, float]
    candidate_scores: dict[str, float]
    delta: dict[str, float] = field(default_factory=dict)
    regression: bool = False
    failing_metrics: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.delta = {
            k: round(self.candidate_scores.get(k, 0.0) - self.baseline_scores.get(k, 0.0), 4)
            for k in self.baseline_scores
        }
        self.failing_metrics = [
            k for k, d in self.delta.items()
            if d < REGRESSION_THRESHOLDS.get(k, -0.03)
        ]
        self.regression = bool(self.failing_metrics)


def evaluate_with_variance(
    scores: list[float],
    expected_threshold: float,
    metric: str = "score",
    n_bootstrap: int = 1000,
    rng_seed: int = 42,
) -> VarianceReport:
    """Evalúa N scores y reporta distribución con IC95 bootstrap.

    El gate pasa si la mediana supera el umbral Y el IC95 bajo supera
    el umbral menos ACCEPTANCE_MARGIN.
    """
    if not scores:
        raise ValueError("scores no puede estar vacío")

    arr = np.array(scores, dtype=float)
    median = float(np.median(arr))

    rng = np.random.default_rng(rng_seed)
    boots = [
        np.median(rng.choice(arr, size=len(arr), replace=True))
        for _ in range(n_bootstrap)
    ]
    ci_low = float(np.percentile(boots, 2.5))
    ci_high = float(np.percentile(boots, 97.5))
    iqr = float(np.percentile(arr, 75) - np.percentile(arr, 25))

    passed = (
        median >= expected_threshold
        and ci_low >= expected_threshold - ACCEPTANCE_MARGIN
    )

    return VarianceReport(
        metric=metric,
        median=round(median, 4),
        ci95_low=round(ci_low, 4),
        ci95_high=round(ci_high, 4),
        iqr=round(iqr, 4),
        passed=passed,
        n_runs=len(scores),
        expected_threshold=expected_threshold,
    )


def compare_pairwise(
    baseline: dict[str, float],
    candidate: dict[str, float],
) -> PairwiseRegressionReport:
    """Compara prompt baseline vs candidato por métricas.

    Regression si cualquier delta < umbral de Tabla 21.1.
    """
    return PairwiseRegressionReport(
        baseline_scores=baseline,
        candidate_scores=candidate,
    )
