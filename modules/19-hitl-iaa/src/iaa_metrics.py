"""Métricas de Inter-Annotator Agreement (Cap. 31 del Manual v13).

Implementación interna determinista sin dependencias externas. Para producción
real, considerar `scikit-learn` (Cohen κ), `krippendorff` o `irrCAC` (Krippendorff α).
Aquí evitamos esas deps para mantener los tests ligeros y reproducibles.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class IAAResult:
    """Resultado de un cálculo de IAA."""

    metric: str
    value: float
    interpretation: str
    n_items: int
    n_annotators: int


# Umbrales canónicos del Manual v13 §31.2 (Landis & Koch 1977; Krippendorff 2018).
KAPPA_THRESHOLDS = {
    "poor": (0.0, 0.20),
    "fair": (0.21, 0.40),
    "moderate": (0.41, 0.60),
    "substantial": (0.61, 0.80),
    "almost_perfect": (0.81, 1.00),
}

# Umbral mínimo aceptable: κ/α ≥ 0.667. Para datasets críticos en alto riesgo, ≥ 0.80.
MIN_ACCEPTABLE_KAPPA = 0.667
HIGH_RISK_KAPPA = 0.80


def interpret_kappa(kappa: float) -> str:
    """Clasificación de Landis & Koch (1977)."""
    if kappa < 0:
        return "worse_than_chance"
    for label, (lo, hi) in KAPPA_THRESHOLDS.items():
        if lo <= kappa <= hi:
            return label
    return "out_of_range"


def cohen_kappa(annotator_a: list[str], annotator_b: list[str]) -> IAAResult:
    """κ de Cohen para dos anotadores con etiquetas categóricas.

    κ = (P_o - P_e) / (1 - P_e)
    P_o = acuerdo observado; P_e = acuerdo esperado por azar.
    """
    if len(annotator_a) != len(annotator_b):
        raise ValueError(
            f"Longitudes distintas: a={len(annotator_a)}, b={len(annotator_b)}"
        )
    if not annotator_a:
        raise ValueError("Listas vacías")
    n = len(annotator_a)
    p_o = sum(1 for a, b in zip(annotator_a, annotator_b, strict=True) if a == b) / n
    # Acuerdo esperado por azar: suma de productos marginales por categoría.
    labels = set(annotator_a) | set(annotator_b)
    count_a = Counter(annotator_a)
    count_b = Counter(annotator_b)
    p_e = sum((count_a[lab] / n) * (count_b[lab] / n) for lab in labels)
    if p_e == 1.0:
        # Anotadores concuerdan en todo y solo hay una clase: κ degenerado, devolver 1.
        return IAAResult("cohen_kappa", 1.0, "almost_perfect", n, 2)
    kappa = (p_o - p_e) / (1 - p_e)
    return IAAResult("cohen_kappa", kappa, interpret_kappa(kappa), n, 2)


def fleiss_kappa(annotations: list[list[str]]) -> IAAResult:
    """Fleiss κ para N ≥ 3 anotadores con etiquetas categóricas.

    annotations: lista por ítem, cada uno con las etiquetas de los N anotadores.
    """
    if not annotations:
        raise ValueError("Lista vacía")
    n_items = len(annotations)
    n_raters = len(annotations[0])
    if n_raters < 3:
        raise ValueError("Fleiss κ requiere ≥ 3 anotadores; usa Cohen κ con 2.")
    if any(len(row) != n_raters for row in annotations):
        raise ValueError("Filas con número distinto de anotadores")

    # Matriz n_items × n_categorías: cuántos anotadores eligieron cada categoría por ítem.
    categories = sorted({label for row in annotations for label in row})
    table = [[row.count(c) for c in categories] for row in annotations]

    # P_j: proporción global de asignaciones a la categoría j.
    total_assignments = n_items * n_raters
    p_j = [sum(row[j] for row in table) / total_assignments for j in range(len(categories))]
    # P_i: nivel de acuerdo dentro del ítem i.
    p_i = [
        (sum(n_ij * (n_ij - 1) for n_ij in row)) / (n_raters * (n_raters - 1))
        for row in table
    ]
    p_bar = sum(p_i) / n_items
    p_e_bar = sum(pj * pj for pj in p_j)
    if p_e_bar == 1.0:
        return IAAResult("fleiss_kappa", 1.0, "almost_perfect", n_items, n_raters)
    kappa = (p_bar - p_e_bar) / (1 - p_e_bar)
    return IAAResult("fleiss_kappa", kappa, interpret_kappa(kappa), n_items, n_raters)


def krippendorff_alpha_nominal(annotations: list[list[str | None]]) -> IAAResult:
    """Krippendorff α para etiquetas nominales con N anotadores y missing values.

    annotations: lista por ítem; cada entrada con N etiquetas (None permitido).
    El cálculo nominal usa la función de distancia δ_nominal: 0 si iguales, 1 si distintos.
    """
    if not annotations:
        raise ValueError("Lista vacía")
    n_raters = len(annotations[0])
    if n_raters < 2:
        raise ValueError("Necesarios ≥ 2 anotadores")

    # Filtrar ítems con < 2 anotaciones presentes
    pairs_total = 0
    pair_distance_sum = 0.0
    values: list[str] = []
    for row in annotations:
        present = [v for v in row if v is not None]
        m_u = len(present)
        if m_u < 2:
            continue
        values.extend(present)
        # Suma de δ sobre todos los pares ordenados (i, j), i != j
        for i in range(m_u):
            for j in range(m_u):
                if i == j:
                    continue
                pair_distance_sum += 0.0 if present[i] == present[j] else 1.0
        pairs_total += m_u * (m_u - 1)

    if pairs_total == 0:
        return IAAResult("krippendorff_alpha_nominal", 0.0, "poor", len(annotations), n_raters)

    d_o = pair_distance_sum / pairs_total

    # d_e: distancia esperada por azar = 1 - Σ p_i^2
    counts = Counter(values)
    n = sum(counts.values())
    d_e = 1.0 - sum((c / n) ** 2 for c in counts.values())
    if d_e == 0:
        return IAAResult(
            "krippendorff_alpha_nominal", 1.0, "almost_perfect", len(annotations), n_raters
        )

    alpha = 1.0 - (d_o / d_e)
    return IAAResult(
        "krippendorff_alpha_nominal", alpha, interpret_kappa(alpha), len(annotations), n_raters
    )


def icc_2way_random(ratings: list[list[float]]) -> IAAResult:
    """ICC(2,1) — Intraclass Correlation Coefficient para anotaciones continuas.

    Implementación simplificada de la versión "two-way random, single measures"
    apropiada para fiabilidad entre N anotadores midiendo K ítems en escala continua.
    Para casos críticos, usar pingouin o scipy.

    ratings: lista por ítem, cada uno con N puntuaciones continuas.
    """
    if not ratings:
        raise ValueError("Lista vacía")
    n_items = len(ratings)
    n_raters = len(ratings[0])
    if n_raters < 2:
        raise ValueError("Necesarios ≥ 2 anotadores")
    if any(len(row) != n_raters for row in ratings):
        raise ValueError("Filas con número distinto de anotadores")

    grand_mean = sum(sum(row) for row in ratings) / (n_items * n_raters)
    row_means = [sum(row) / n_raters for row in ratings]
    col_means = [
        sum(ratings[i][j] for i in range(n_items)) / n_items for j in range(n_raters)
    ]

    ss_b = n_raters * sum((m - grand_mean) ** 2 for m in row_means)
    ss_w = sum(sum((ratings[i][j] - row_means[i]) ** 2 for j in range(n_raters)) for i in range(n_items))
    ss_c = n_items * sum((c - grand_mean) ** 2 for c in col_means)
    ss_e = ss_w - ss_c

    ms_b = ss_b / max(n_items - 1, 1)
    ms_c = ss_c / max(n_raters - 1, 1)
    ms_e = ss_e / max((n_items - 1) * (n_raters - 1), 1)

    denom = ms_b + (n_raters - 1) * ms_e + (n_raters / n_items) * (ms_c - ms_e)
    if denom == 0:
        return IAAResult("icc_2way_random", 0.0, "poor", n_items, n_raters)
    icc = (ms_b - ms_e) / denom
    icc = max(min(icc, 1.0), 0.0)
    # ICC interpretación: ≥0.75 buena fiabilidad (Cicchetti 1994)
    if icc < 0.40:
        label = "poor"
    elif icc < 0.60:
        label = "fair"
    elif icc < 0.75:
        label = "good"
    else:
        label = "excellent"
    return IAAResult("icc_2way_random", icc, label, n_items, n_raters)


def assert_acceptable_iaa(
    result: IAAResult, min_value: float = MIN_ACCEPTABLE_KAPPA, high_risk: bool = False
) -> None:
    """Eleva ValueError si el IAA no alcanza el umbral.

    Usa raise (no assert) para sobrevivir a `python -O` (Manual §28.4).
    high_risk=True ⇒ exigir ≥ 0.80 (datasets críticos).
    """
    threshold = HIGH_RISK_KAPPA if high_risk else min_value
    if result.value < threshold:
        raise ValueError(
            f"IAA insuficiente: {result.metric}={result.value:.3f} < {threshold} "
            f"(n_items={result.n_items}, n_annotators={result.n_annotators}). "
            "Recalibrar guidelines y reentrenar anotadores."
        )
