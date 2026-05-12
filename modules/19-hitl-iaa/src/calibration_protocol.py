"""Protocolo de calibración de anotadores en 6 fases (Manual v13 §31.4)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class CalibrationPhase(StrEnum):
    GUIDELINES = "guidelines"
    PILOT = "pilot"
    DISCUSSION = "discussion"
    RE_ANNOTATION = "re_annotation"
    CERTIFICATION = "certification"
    RE_CALIBRATION = "re_calibration"


@dataclass(frozen=True)
class PhaseResult:
    phase: CalibrationPhase
    success: bool
    output: str
    notes: str = ""


@dataclass
class CalibrationReport:
    """Resultado completo del protocolo de 6 fases."""

    phases: list[PhaseResult] = field(default_factory=list)

    def add(self, result: PhaseResult) -> None:
        self.phases.append(result)

    @property
    def all_passed(self) -> bool:
        return all(p.success for p in self.phases)

    @property
    def failed_phase(self) -> CalibrationPhase | None:
        for p in self.phases:
            if not p.success:
                return p.phase
        return None


def run_calibration(
    n_pilot_items: int,
    pilot_iaa: float,
    after_discussion_iaa: float,
    final_iaa: float,
    target_iaa: float = 0.70,
) -> CalibrationReport:
    """Ejecuta el protocolo simulado de calibración con métricas observadas.

    Cada fase tiene un criterio de éxito explícito (§31.4 Tabla 31.2).
    """
    report = CalibrationReport()

    # 1. Guidelines: presupuesto. Asumimos siempre listo si hay rúbrica.
    report.add(
        PhaseResult(
            CalibrationPhase.GUIDELINES,
            success=True,
            output="Documento de etiquetado redactado",
        )
    )

    # 2. Pilot: 20-50 items con todos los anotadores
    pilot_pass = 20 <= n_pilot_items <= 50
    report.add(
        PhaseResult(
            CalibrationPhase.PILOT,
            success=pilot_pass,
            output=f"Primer IAA={pilot_iaa:.3f} sobre n={n_pilot_items}",
            notes="Tamaño piloto fuera de 20-50 items" if not pilot_pass else "",
        )
    )

    # 3. Discussion: resolver desacuerdos; IAA tras discusión debe mejorar
    disc_pass = after_discussion_iaa > pilot_iaa
    report.add(
        PhaseResult(
            CalibrationPhase.DISCUSSION,
            success=disc_pass,
            output=f"IAA tras discusión={after_discussion_iaa:.3f}",
        )
    )

    # 4. Re-annotation: con guidelines v2, IAA final debe alcanzar target
    re_pass = final_iaa >= target_iaa
    report.add(
        PhaseResult(
            CalibrationPhase.RE_ANNOTATION,
            success=re_pass,
            output=f"IAA final={final_iaa:.3f} vs target={target_iaa:.3f}",
        )
    )

    # 5. Certification: cada anotador certificado si IAA personal >= 0.70 con consenso
    cert_pass = final_iaa >= 0.70
    report.add(
        PhaseResult(
            CalibrationPhase.CERTIFICATION,
            success=cert_pass,
            output="Equipo calibrado" if cert_pass else "Equipo NO calibrado",
        )
    )

    # 6. Re-calibration: cadencia trimestral (siempre pendiente)
    report.add(
        PhaseResult(
            CalibrationPhase.RE_CALIBRATION,
            success=True,
            output="Re-calibración programada trimestralmente",
        )
    )

    return report
