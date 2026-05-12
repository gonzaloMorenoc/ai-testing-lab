"""Simulador del incidente D.8: caída de faithfulness tras release v3.2.

Reproduce la línea de tiempo T+0 → T+40min del manual:
- T+0: alerta PagerDuty cuando faithfulness cae bajo 0.80 mantenida 15 min.
- T+5: comparar versiones; bisección apunta al prompt v3.2.
- T+15: regression suite del prompt (§24) muestra Δ faithfulness = -0.15.
  Investigación: el gate de PR (0.85) estaba inadvertidamente desactivado
  tras un merge conflictivo. AP-10 + OP-09 confirmados.
- T+25: rollback al prompt v3.1.
- T+40: feature flag bloquea v3.2.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IncidentSnapshot:
    """Estado del sistema en un momento concreto."""

    timestamp_minutes: int
    prompt_version: str
    faithfulness: float
    refusal_rate: float
    alert_status: str
    runbook_step: str


# Línea de tiempo canónica del incidente (Manual §D.8).
INCIDENT_TIMELINE: tuple[IncidentSnapshot, ...] = (
    IncidentSnapshot(0, "v3.2", 0.76, 0.93, "FIRING", "alerta_pagerduty"),
    IncidentSnapshot(5, "v3.2", 0.76, 0.93, "FIRING", "comparar_versions"),
    IncidentSnapshot(15, "v3.2", 0.76, 0.93, "FIRING", "regression_suite_confirma"),
    IncidentSnapshot(25, "v3.1", 0.90, 0.99, "RESOLVED", "rollback"),
    IncidentSnapshot(40, "v3.1", 0.91, 0.99, "RESOLVED", "feature_flag_blocks_v3_2"),
)

# Umbrales del incidente
FAITHFULNESS_BASELINE = 0.91
FAITHFULNESS_INCIDENT = 0.76
FAITHFULNESS_AUTO_ROLLBACK = 0.80


def should_trigger_alert(faithfulness: float, sustained_minutes: int) -> bool:
    """Regla de alerta D.8: faithfulness < 0.80 mantenida 15 min."""
    return faithfulness < FAITHFULNESS_AUTO_ROLLBACK and sustained_minutes >= 15


def diagnose_root_cause(
    prompt_changed: bool, model_changed: bool, corpus_changed: bool
) -> str:
    """Bisección en T+5 (D.8): qué componente cambió entre baseline y release."""
    changes = []
    if prompt_changed:
        changes.append("prompt")
    if model_changed:
        changes.append("model")
    if corpus_changed:
        changes.append("corpus")
    if len(changes) == 0:
        return "no_changes_detected_check_provider_drift"
    if len(changes) == 1:
        return changes[0]
    return f"multiple_changes_{'+'.join(changes)}"


def reproduce_incident() -> dict[str, float | str]:
    """Reproduce el estado del incidente: prompt v3.2 introduce regresión."""
    return {
        "prompt_version_pre": "v3.1",
        "prompt_version_incident": "v3.2",
        "faithfulness_pre": FAITHFULNESS_BASELINE,
        "faithfulness_post": FAITHFULNESS_INCIDENT,
        "delta_faithfulness": FAITHFULNESS_INCIDENT - FAITHFULNESS_BASELINE,
        "refusal_rate_pre": 0.99,
        "refusal_rate_post": 0.93,
        "root_cause": "tone_change_degrades_citation_use",
        "gate_violation": "ap10_op09_pr_gate_disabled_after_merge_conflict",
    }
