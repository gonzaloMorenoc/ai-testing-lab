"""AP-01 .. AP-10: Detección determinista de anti-patterns de evaluación LLM.

Sin LLM, sin APIs externas.  Basado en Manual QA AI v12, Capítulo 19.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


# ── Tipos base ──────────────────────────────────────────────────────────────


class AntiPatternSeverity(StrEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"


@dataclass(frozen=True)
class AntiPatternViolation:
    ap_id: str
    name: str
    description: str
    severity: AntiPatternSeverity
    details: str


@dataclass(frozen=True)
class EvalDesignReport:
    violations: tuple[AntiPatternViolation, ...]
    passed: bool
    total_checks: int = 10

    @property
    def critical_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == AntiPatternSeverity.CRITICAL)

    @property
    def high_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == AntiPatternSeverity.HIGH)


# ── Checks individuales ──────────────────────────────────────────────────────

_NEGATIVE_KEYWORDS = frozenset({"refuse", "cannot", "n/a", "error"})


def check_ap01_happy_path_only(
    test_cases: list[dict],
    required_negative_fraction: float = 0.15,
) -> AntiPatternViolation | None:
    """AP-01: Evaluar solo el happy path."""
    if not test_cases:
        return None

    negative_count = 0
    for case in test_cases:
        meta = case.get("metadata", {}) or {}
        if meta.get("expected_negative", False):
            negative_count += 1
            continue
        expected = str(case.get("expected_output", "")).lower()
        if any(kw in expected for kw in _NEGATIVE_KEYWORDS):
            negative_count += 1

    fraction = negative_count / len(test_cases)
    if fraction < required_negative_fraction:
        return AntiPatternViolation(
            ap_id="AP-01",
            name="Happy Path Only",
            description="El test set evalúa solo el camino feliz sin casos negativos.",
            severity=AntiPatternSeverity.HIGH,
            details=(
                f"Fracción de casos negativos: {fraction:.2%} "
                f"(mínimo requerido: {required_negative_fraction:.2%})"
            ),
        )
    return None


def check_ap02_data_contamination(
    train_inputs: list[str],
    test_inputs: list[str],
    overlap_threshold: float = 0.1,
) -> AntiPatternViolation | None:
    """AP-02: Dataset de test contaminado con training."""
    if not test_inputs:
        return None

    train_set = {s.lower() for s in train_inputs}
    overlapping = sum(1 for t in test_inputs if t.lower() in train_set)
    fraction = overlapping / len(test_inputs)

    if fraction > overlap_threshold:
        return AntiPatternViolation(
            ap_id="AP-02",
            name="Data Contamination",
            description="El dataset de test contiene inputs que también están en training.",
            severity=AntiPatternSeverity.HIGH,
            details=(
                f"Overlap: {overlapping}/{len(test_inputs)} casos "
                f"({fraction:.2%}), umbral: {overlap_threshold:.2%}"
            ),
        )
    return None


def check_ap03_no_baseline(
    baseline_score: float | None,
) -> AntiPatternViolation | None:
    """AP-03: Sin baseline de comparación."""
    if baseline_score is None:
        return AntiPatternViolation(
            ap_id="AP-03",
            name="No Baseline",
            description="No existe un score de referencia contra el que comparar regresiones.",
            severity=AntiPatternSeverity.CRITICAL,
            details="baseline_score es None — sin baseline no es posible detectar regresiones.",
        )
    return None


def check_ap04_insufficient_sample_size(
    n_samples: int,
    min_samples: int = 30,
) -> AntiPatternViolation | None:
    """AP-04: Test set demasiado pequeño para significación estadística."""
    if n_samples < min_samples:
        return AntiPatternViolation(
            ap_id="AP-04",
            name="Insufficient Sample Size",
            description="El test set es demasiado pequeño para inferencia estadística fiable.",
            severity=AntiPatternSeverity.HIGH,
            details=f"n={n_samples} muestras (mínimo requerido: {min_samples}).",
        )
    return None


def check_ap05_judge_equals_generator(
    generator_model_id: str,
    judge_model_id: str,
) -> AntiPatternViolation | None:
    """AP-05: Mismo LLM como generador y juez."""
    if generator_model_id.lower() == judge_model_id.lower():
        return AntiPatternViolation(
            ap_id="AP-05",
            name="Judge Equals Generator",
            description="El mismo modelo genera las respuestas y actúa como juez.",
            severity=AntiPatternSeverity.CRITICAL,
            details=(
                f"generator_model_id='{generator_model_id}' == "
                f"judge_model_id='{judge_model_id}' — introduce sesgo de auto-complacencia."
            ),
        )
    return None


def check_ap06_ignores_production_distribution(
    test_cases: list[dict],
    prod_metadata_key: str = "risk_tier",
) -> AntiPatternViolation | None:
    """AP-06: Ignorar distribución de producción en el test set."""
    if not test_cases:
        return None

    has_key = any(
        prod_metadata_key in (case.get("metadata") or {})
        for case in test_cases
    )
    if not has_key:
        return AntiPatternViolation(
            ap_id="AP-06",
            name="Ignores Production Distribution",
            description="El test set no refleja la distribución de producción.",
            severity=AntiPatternSeverity.MEDIUM,
            details=(
                f"Ningún caso contiene metadata.{prod_metadata_key}. "
                "Los datasets bien diseñados incluyen risk_tier, domain o language."
            ),
        )
    return None


_EMPIRICAL_THRESHOLDS: frozenset[float] = frozenset(
    {0.70, 0.75, 0.80, 0.85, 0.90, 0.92, 0.95, 0.98, 0.99}
)


def check_ap07_arbitrary_threshold(
    threshold: float,
    known_empirical_thresholds: tuple[float, ...] = (
        0.70, 0.75, 0.80, 0.85, 0.90, 0.92, 0.95, 0.98, 0.99
    ),
) -> AntiPatternViolation | None:
    """AP-07: Threshold arbitrario sin validación empírica."""
    empirical = frozenset(known_empirical_thresholds)
    if threshold not in empirical:
        return AntiPatternViolation(
            ap_id="AP-07",
            name="Arbitrary Threshold",
            description="El threshold de aprobación no tiene respaldo empírico.",
            severity=AntiPatternSeverity.MEDIUM,
            details=(
                f"threshold={threshold} no está entre los valores empíricos conocidos: "
                f"{sorted(empirical)}"
            ),
        )
    return None


def _has_adversarial_signal(text: str) -> bool:
    """Detecta señales de input adversarial en el texto."""
    if len(text) < 10:
        return True
    upper_fraction = sum(1 for c in text if c.isupper()) / max(len(text), 1)
    if upper_fraction > 0.70:
        return True
    if any(ord(c) > 127 for c in text):
        return True
    return False


def check_ap08_no_adversarial_cases(
    test_cases: list[dict],
) -> AntiPatternViolation | None:
    """AP-08: Sin edge cases ni inputs adversariales."""
    if not test_cases:
        return None

    for case in test_cases:
        meta = case.get("metadata") or {}
        if meta.get("adversarial") or meta.get("edge_case"):
            return None
        text = str(case.get("input", ""))
        if _has_adversarial_signal(text):
            return None

    return AntiPatternViolation(
        ap_id="AP-08",
        name="No Adversarial Cases",
        description="El test set carece de edge cases o inputs adversariales.",
        severity=AntiPatternSeverity.HIGH,
        details=(
            "Ningún caso tiene metadata.adversarial=True, metadata.edge_case=True, "
            "ni señales adversariales en el input (emojis, mayúsculas extremas, texto corto)."
        ),
    )


_PERCENTILE_KEYS = frozenset({"p50", "p95", "p99", "median"})


def check_ap09_latency_mean_only(
    latency_stats: dict,
) -> AntiPatternViolation | None:
    """AP-09: Latencia reportada solo con media, sin percentiles."""
    if not latency_stats:
        return AntiPatternViolation(
            ap_id="AP-09",
            name="Latency Mean Only",
            description="No se reportan estadísticas de latencia.",
            severity=AntiPatternSeverity.HIGH,
            details="latency_stats está vacío — no hay información de latencia.",
        )

    has_mean = "mean" in latency_stats
    has_percentile = bool(_PERCENTILE_KEYS & latency_stats.keys())

    if has_mean and not has_percentile:
        return AntiPatternViolation(
            ap_id="AP-09",
            name="Latency Mean Only",
            description="La latencia se reporta solo con la media, sin percentiles de cola.",
            severity=AntiPatternSeverity.HIGH,
            details=(
                "latency_stats contiene 'mean' pero falta al menos uno de: "
                f"{sorted(_PERCENTILE_KEYS)}. Los percentiles p95/p99 son críticos."
            ),
        )
    return None


def check_ap10_no_variance_measurement(
    n_runs: int,
    has_variance_report: bool = False,
    min_runs: int = 3,
) -> AntiPatternViolation | None:
    """AP-10: Reproducibilidad ignorada."""
    if n_runs < min_runs and not has_variance_report:
        return AntiPatternViolation(
            ap_id="AP-10",
            name="No Variance Measurement",
            description="La evaluación no mide varianza entre ejecuciones.",
            severity=AntiPatternSeverity.HIGH,
            details=(
                f"n_runs={n_runs} (mínimo: {min_runs}) y has_variance_report=False. "
                "temperatura=0 no garantiza determinismo absoluto."
            ),
        )
    return None


# ── Checker principal ────────────────────────────────────────────────────────


class EvalDesignChecker:
    """Ejecuta los 10 checks de anti-patterns y devuelve un EvalDesignReport."""

    def check_all(
        self,
        *,
        test_cases: list[dict] | None = None,
        train_inputs: list[str] | None = None,
        baseline_score: float | None = None,
        n_samples: int = 0,
        generator_model_id: str = "",
        judge_model_id: str = "",
        threshold: float = 0.7,
        latency_stats: dict | None = None,
        n_runs: int = 1,
        has_variance_report: bool = False,
    ) -> EvalDesignReport:
        """Ejecuta los 10 checks y retorna EvalDesignReport.

        Los checks sin datos suficientes se saltan silenciosamente.
        passed = no hay violaciones CRITICAL ni HIGH.
        """
        violations: list[AntiPatternViolation] = []

        _cases = test_cases or []
        _train = train_inputs or []
        _latency = latency_stats if latency_stats is not None else {}

        candidates = [
            check_ap01_happy_path_only(_cases) if _cases else None,
            check_ap02_data_contamination(_train, [c.get("input", "") for c in _cases])
            if _cases and _train
            else None,
            check_ap03_no_baseline(baseline_score),
            check_ap04_insufficient_sample_size(n_samples) if n_samples > 0 else None,
            check_ap05_judge_equals_generator(generator_model_id, judge_model_id)
            if generator_model_id and judge_model_id
            else None,
            check_ap06_ignores_production_distribution(_cases) if _cases else None,
            check_ap07_arbitrary_threshold(threshold),
            check_ap08_no_adversarial_cases(_cases) if _cases else None,
            check_ap09_latency_mean_only(_latency),
            check_ap10_no_variance_measurement(n_runs, has_variance_report),
        ]

        violations = [v for v in candidates if v is not None]
        blocking = {AntiPatternSeverity.CRITICAL, AntiPatternSeverity.HIGH}
        passed = not any(v.severity in blocking for v in violations)

        return EvalDesignReport(
            violations=tuple(violations),
            passed=passed,
        )
