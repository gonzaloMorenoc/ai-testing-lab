from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class JudgeBiasType(StrEnum):
    """Los 5 sesgos principales del LLM-as-Judge (Tabla 5.1 del Manual QA AI v12)."""

    VERBOSITY = "verbosity"  # prefiere respuestas largas aunque sean peores
    SELF_ENHANCEMENT = "self_enhancement"  # el mismo LLM evaluado y evaluador
    POSITION = "position"  # prefiere la respuesta que aparece primero
    LENIENT = "lenient"  # sistemáticamente generoso con todos
    FORMAT = "format"  # prefiere respuestas bien formateadas (markdown, listas)


@dataclass(frozen=True)
class BiasDetectionResult:
    bias_type: JudgeBiasType
    detected: bool
    evidence: str
    severity: float  # 0.0-1.0


def detect_verbosity_bias(
    score_short: float, score_long: float, length_ratio: float
) -> BiasDetectionResult:
    """Detecta verbosity bias: score_long > score_short desproporcionadamente.

    length_ratio = len(long_response) / len(short_response). Si > 2x y delta > 0.15 → bias probable.
    """
    delta = score_long - score_short
    detected = length_ratio > 2.0 and delta > 0.15
    return BiasDetectionResult(
        bias_type=JudgeBiasType.VERBOSITY,
        detected=detected,
        evidence=f"length_ratio={length_ratio:.2f}, score_delta={delta:.3f}",
        severity=round(min(1.0, delta * 2) if detected else 0.0, 3),
    )


def detect_position_bias(score_ab: float, score_ba: float) -> BiasDetectionResult:
    """Detecta position bias: el mismo par evaluado en orden A→B y B→A da resultados distintos.

    bias_delta > 0.05 indica sensibilidad al orden (§5.2, calibrate_for_position_bias).
    """
    bias_delta = abs(score_ab - score_ba)
    detected = bias_delta > 0.05
    return BiasDetectionResult(
        bias_type=JudgeBiasType.POSITION,
        detected=detected,
        evidence=f"bias_delta={bias_delta:.4f} (AB={score_ab:.3f}, BA={score_ba:.3f})",
        severity=round(min(1.0, bias_delta * 10) if detected else 0.0, 3),
    )


# --- Inter-Annotator Agreement (Cap 28) ---


@dataclass(frozen=True)
class IAAResult:
    metric_name: str
    score: float
    n_items: int
    interpretation: str

    @property
    def acceptable(self) -> bool:
        return self.score >= 0.61  # κ mínimo aceptable (Tabla 28.1)

    @property
    def high_quality(self) -> bool:
        return self.score >= 0.80  # casi perfecto (Tabla 28.1)


def cohen_kappa(annotations_a: list[int], annotations_b: list[int]) -> IAAResult:
    """κ de Cohen para 2 anotadores con etiquetas categóricas.

    Umbral: ≥ 0.61 sustancial; ≥ 0.81 casi perfecto (Landis & Koch 1977).
    """
    if len(annotations_a) != len(annotations_b):
        raise ValueError("Las listas de anotaciones deben tener la misma longitud")
    if not annotations_a:
        raise ValueError("Las anotaciones no pueden estar vacías")

    n = len(annotations_a)
    categories = sorted(set(annotations_a) | set(annotations_b))

    # Acuerdo observado
    po = sum(a == b for a, b in zip(annotations_a, annotations_b, strict=False)) / n

    # Acuerdo esperado por azar
    pe = 0.0
    for cat in categories:
        pa = annotations_a.count(cat) / n
        pb = annotations_b.count(cat) / n
        pe += pa * pb

    kappa = 1.0 if pe >= 1.0 else round((po - pe) / (1.0 - pe), 4)

    if kappa >= 0.81:
        interp = "casi perfecto"
    elif kappa >= 0.61:
        interp = "sustancial"
    elif kappa >= 0.41:
        interp = "moderado"
    else:
        interp = "débil — recalibrar guidelines"

    return IAAResult(metric_name="cohen_kappa", score=kappa, n_items=n, interpretation=interp)
