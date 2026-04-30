from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from scipy.stats import ks_2samp


@dataclass(frozen=True)
class DriftReport:
    """Resultado del detector de deriva semántica (§10.3 Manual QA AI v12)."""

    historical_mean: float
    current_mean: float
    mean_drop: float
    ci95_low: float
    ci95_high: float
    ks_statistic: float
    ks_pvalue: float
    distribution_changed: bool  # p_KS < 0.01
    quality_degraded: bool  # mean_drop < -0.03
    drift_detected: bool  # AMBOS criterios: distribución cambió Y calidad bajó
    min_similarity: float
    affected_count: int  # docs bajo threshold


def _validate_inputs(
    baseline_scores: list[float],
    current_scores: list[float],
    hist: np.ndarray,
) -> None:
    if len(baseline_scores) != len(current_scores):
        raise ValueError(
            f"Longitudes distintas: baseline={len(baseline_scores)}, "
            f"current={len(current_scores)}. Deben corresponder a las mismas queries."
        )
    if hist.size < 30:
        raise ValueError(
            f"historical_scores insuficiente ({hist.size}). "
            "Recomendado >= 30 muestras para que el KS tenga potencia."
        )


def _bootstrap_ci(
    scores: np.ndarray,
    n_bootstrap: int,
    rng: np.random.Generator,
) -> tuple[float, float]:
    boots = [
        rng.choice(scores, size=len(scores), replace=True).mean()
        for _ in range(n_bootstrap)
    ]
    return float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


def detect_semantic_drift(
    baseline_scores: list[float],
    current_scores: list[float],
    historical_scores: np.ndarray | None = None,
    threshold: float = 0.85,
    n_bootstrap: int = 1000,
    rng_seed: int = 42,
) -> DriftReport:
    """Detecta deriva semántica con baseline histórica + bootstrap + KS de dos muestras.

    Requiere len(baseline_scores) == len(current_scores).
    historical_scores: distribución de referencia empírica (ventana N-1).
    Si no se provee, se usa baseline_scores como referencia (degraded mode).
    """
    hist = np.array(
        historical_scores if historical_scores is not None else baseline_scores,
        dtype=float,
    )

    _validate_inputs(baseline_scores, current_scores, hist)

    scores = np.array(current_scores, dtype=float)
    rng = np.random.default_rng(rng_seed)

    ci_low, ci_high = _bootstrap_ci(scores, n_bootstrap, rng)
    ks_stat, ks_p = ks_2samp(scores, hist)
    mean_drop = float(scores.mean() - hist.mean())

    return DriftReport(
        historical_mean=float(hist.mean()),
        current_mean=float(scores.mean()),
        mean_drop=round(mean_drop, 4),
        ci95_low=round(ci_low, 4),
        ci95_high=round(ci_high, 4),
        ks_statistic=round(float(ks_stat), 4),
        ks_pvalue=round(float(ks_p), 4),
        distribution_changed=bool(ks_p < 0.01),
        quality_degraded=bool(mean_drop < -0.03),
        drift_detected=bool(ks_p < 0.01 and mean_drop < -0.03),
        min_similarity=float(scores.min()),
        affected_count=int((scores < threshold).sum()),
    )
