"""Cálculo de tamaño muestral para detectar diferencias entre sistemas (Manual v13 §31.6).

Referencias aproximadas, no recetas universales. Para casos críticos usar
statsmodels o G*Power.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import ceil


class EffectSize(StrEnum):
    LARGE = "large"      # Cohen's d ≥ 0.5
    MEDIUM = "medium"    # Cohen's d ≈ 0.3
    SMALL = "small"      # Cohen's d ≤ 0.1


# Tabla §31.6 (alpha=0.05, power≥0.8). Pareadas / no pareadas.
_SAMPLE_SIZES: dict[EffectSize, tuple[int, int]] = {
    EffectSize.LARGE: (100, 200),
    EffectSize.MEDIUM: (300, 500),
    EffectSize.SMALL: (1000, 1500),
}


@dataclass(frozen=True)
class SampleSizeRecommendation:
    effect_size: EffectSize
    paired_n: int
    unpaired_n: int
    rationale: str


def recommend_sample_size(
    effect_size: EffectSize, paired: bool = True
) -> SampleSizeRecommendation:
    """Devuelve el tamaño muestral recomendado.

    paired=True: las dos versiones se evalúan en los mismos ítems (más eficiente).
    """
    paired_n, unpaired_n = _SAMPLE_SIZES[effect_size]
    return SampleSizeRecommendation(
        effect_size=effect_size,
        paired_n=paired_n,
        unpaired_n=unpaired_n,
        rationale=(
            f"Para diferencias {effect_size.value} con α=0.05 y power≥0.8: "
            f"pareadas={paired_n}, no pareadas={unpaired_n}. "
            "Si las muestras son pareadas, usar test pareado (Wilcoxon/paired t)."
        ),
    )


def n_for_proportion_comparison(
    p1: float, p2: float, alpha: float = 0.05, power: float = 0.80
) -> int:
    """Tamaño muestral aproximado para comparar dos proporciones (Chi² / Fisher).

    Fórmula simplificada (no exacta, suficiente como guía):
        n ≈ (z_α/2 + z_β)² × (p1(1-p1) + p2(1-p2)) / (p1 - p2)²
    """
    if p1 == p2:
        raise ValueError("p1 y p2 deben ser distintos")
    # z-values aproximados para alpha=0.05 (z=1.96) y power=0.80 (z=0.84).
    # Tabla pequeña para evitar dependencia de scipy.
    z_alpha = {0.05: 1.96, 0.01: 2.576, 0.10: 1.645}.get(alpha, 1.96)
    z_beta = {0.80: 0.842, 0.90: 1.282, 0.95: 1.645}.get(power, 0.842)
    numerator = (z_alpha + z_beta) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2))
    denominator = (p1 - p2) ** 2
    return ceil(numerator / denominator)
