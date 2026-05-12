"""Postmortem y mejoras estructurales (D.10 del Manual v13).

Documenta las cinco mejoras estructurales acordadas tras el incidente:
- Meta-test en CI que falle si faltan gates obligatorios en el workflow.
- Versionado obligatorio del prompt con changelog firmado por QA Lead.
- Alertas dobles: por umbral absoluto y por drift estadístico.
- Auditoría trimestral del checklist de release con revisor externo.
- Robustness suite activada también en PR para idiomas minoritarios.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StructuralImprovement:
    """Acción concreta acordada en el postmortem."""

    name: str
    owner_role: str
    target_layer: str
    prevents: tuple[str, ...]


# D.10 — Mejoras estructurales.
IMPROVEMENTS: tuple[StructuralImprovement, ...] = (
    StructuralImprovement(
        name="meta_test_ci_requires_obligatory_gates",
        owner_role="DevOps",
        target_layer="ci_cd",
        prevents=("AP-10", "OP-09"),
    ),
    StructuralImprovement(
        name="prompt_versioning_with_signed_changelog",
        owner_role="QALead",
        target_layer="prompt_registry",
        prevents=("AP-10",),
    ),
    StructuralImprovement(
        name="dual_alerts_absolute_and_drift",
        owner_role="MLOps",
        target_layer="observability",
        prevents=("AP-06",),
    ),
    StructuralImprovement(
        name="quarterly_release_audit_external_reviewer",
        owner_role="QALead",
        target_layer="process",
        prevents=("AP-07",),
    ),
    StructuralImprovement(
        name="robustness_suite_in_pr_for_minority_languages",
        owner_role="QAEngineer",
        target_layer="robustness",
        prevents=("AP-08",),
    ),
)


def antipatterns_prevented() -> set[str]:
    """Conjunto de antipatrones evitados por el conjunto completo de mejoras."""
    out: set[str] = set()
    for imp in IMPROVEMENTS:
        out.update(imp.prevents)
    return out


@dataclass(frozen=True)
class BugReport:
    """Estructura del bug report D.9."""

    id: str
    date: str
    severity: str
    status: str
    gates_failed: tuple[str, ...]
    metrics_observed: dict[str, float]
    root_cause: str
    remediations: tuple[str, ...]


def build_bug_report() -> BugReport:
    """Reproduce el bug report canónico D.9 del incidente simulado."""
    return BugReport(
        id="INC-2026-0427-001",
        date="2026-04-27",
        severity="high",
        status="resolved",
        gates_failed=("faithfulness_pr_gate_not_executed",),
        metrics_observed={
            "faithfulness_pre": 0.91,
            "faithfulness_post": 0.76,
            "refusal_rate_pre": 0.99,
            "refusal_rate_post": 0.93,
        },
        root_cause=(
            "El gate de PR de faithfulness estaba desactivado tras un merge "
            "conflictivo en .github/workflows/qa-gate.yml. La nueva versión "
            "del prompt (v3.2) introdujo un cambio de tono que degradó la "
            "cita textual de coberturas, aumentando alucinaciones extrínsecas "
            "(Cap. 17)."
        ),
        remediations=(
            "Rollback prompt -> v3.1 (faithfulness 0.90 restaurada)",
            "Re-habilitar gate y añadir test que verifica la presencia de "
            "los gates obligatorios en el workflow (smoke meta-test)",
            "Añadir alerta de drift sobre faithfulness con IC95",
            "Postmortem con acción para AP-10 / OP-09 (registro de gates)",
        ),
    )
