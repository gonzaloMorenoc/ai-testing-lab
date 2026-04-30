from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum


class HallucinationLevel1(StrEnum):
    """Clasificación principal de alucinaciones (Ji et al. 2023)."""

    INTRINSIC = "intrinsic"   # contradice el contexto proporcionado
    EXTRINSIC = "extrinsic"   # añade info no presente ni soportada por el contexto


class HallucinationLevel2(StrEnum):
    """Subcategorías ortogonales (pueden ser intrinsic o extrinsic)."""

    FACTUAL = "factual"       # cita artículo/entidad inexistente
    TEMPORAL = "temporal"     # confunde secuencias, inventa fechas
    NUMERICAL = "numerical"   # cifras incorrectas
    CITATION = "citation"     # atribuye a fuente errónea
    LOGICAL = "logical"       # conclusión no se sigue de las premisas


@dataclass(frozen=True)
class HallucinationReport:
    has_hallucination: bool
    level1: HallucinationLevel1 | None
    level2: HallucinationLevel2 | None
    unsupported_claims: tuple[str, ...]
    confidence: float  # 0.0-1.0

    @property
    def passed(self) -> bool:
        return not self.has_hallucination


@dataclass
class HallucinationClassifier:
    """Clasifica alucinaciones sin LLM usando heurísticos deterministas."""

    # Señales de alucinación temporal
    TEMPORAL_SIGNALS: frozenset[str] = frozenset({
        "yesterday", "tomorrow", "last year", "next year",
        "in 2019", "in 2020", "in 2021", "currently", "recently",
    })
    # Señales de alucinación numérica
    NUMERICAL_PATTERNS_EXTREME: tuple[str, ...] = ("100%", "0%", "never", "always", "every")

    def classify(
        self,
        response: str,
        context: str,
        unsupported_claims: list[str],
    ) -> HallucinationReport:
        """Determina tipo de alucinación a partir de claims no soportados."""
        if not unsupported_claims:
            return HallucinationReport(
                has_hallucination=False,
                level1=None,
                level2=None,
                unsupported_claims=(),
                confidence=1.0,
            )

        response_lower = response.lower()
        context_lower = context.lower()

        # ¿Las claims contradicen el contexto (intrinsic) o lo extienden (extrinsic)?
        level1 = self._detect_level1(unsupported_claims, context_lower)
        level2 = self._detect_level2(response_lower, unsupported_claims)

        confidence = 0.8 if level1 and level2 else 0.6

        return HallucinationReport(
            has_hallucination=True,
            level1=level1,
            level2=level2,
            unsupported_claims=tuple(unsupported_claims),
            confidence=confidence,
        )

    def _detect_level1(self, claims: list[str], context_lower: str) -> HallucinationLevel1:
        for claim in claims:
            claim_words = {w.lower() for w in claim.split() if len(w) > 3}
            if claim_words & set(context_lower.split()):
                return HallucinationLevel1.INTRINSIC
        return HallucinationLevel1.EXTRINSIC

    def _detect_level2(self, response_lower: str, claims: list[str]) -> HallucinationLevel2:
        combined = " ".join(claims).lower()
        if any(sig in combined for sig in self.TEMPORAL_SIGNALS):
            return HallucinationLevel2.TEMPORAL
        if any(pat in combined for pat in self.NUMERICAL_PATTERNS_EXTREME):
            return HallucinationLevel2.NUMERICAL
        if re.search(r"\b\d{4}\b", combined):
            return HallucinationLevel2.FACTUAL
        if any(word in combined for word in ["says", "according to", "states", "reports"]):
            return HallucinationLevel2.CITATION
        return HallucinationLevel2.FACTUAL
