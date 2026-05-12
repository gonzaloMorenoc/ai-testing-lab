"""Solución del ejercicio del módulo 20.

Ejercicio: dado el incidente simulado D.8, ejecutar el runbook completo:
1. Detectar el trigger de alerta.
2. Diagnosticar la causa raíz.
3. Evaluar los gates de cada etapa antes y después del rollback.
4. Generar el bug report.

Modo de uso:
    python exercises/solutions/20-end-to-end-case-solution.py
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "modules" / "20-end-to-end-case" / "src"))
sys.path.insert(0, str(REPO))

from gates_pipeline import Stage, evaluate_stage  # noqa: E402
from incident_simulator import (  # noqa: E402
    diagnose_root_cause,
    reproduce_incident,
    should_trigger_alert,
)
from postmortem import IMPROVEMENTS, build_bug_report  # noqa: E402


def main() -> None:
    print("=== T+0: alerta inicial ===")
    incident = reproduce_incident()
    faith_post = incident["faithfulness_post"]
    trigger = should_trigger_alert(faith_post, sustained_minutes=15)
    print(f"Faithfulness post: {faith_post}")
    print(f"Alerta dispara: {trigger}")
    print()

    print("=== T+5: diagnóstico ===")
    cause = diagnose_root_cause(
        prompt_changed=True, model_changed=False, corpus_changed=False
    )
    print(f"Causa raíz: {cause}")
    print()

    print("=== T+15: gates evaluados retrospectivamente ===")
    observed_v3_2 = {
        "faithfulness": faith_post,
        "answer_correctness": 0.80,
        "context_recall": 0.85,
        "ndcg_at_5": 0.82,
        "safety_canary_leaks": 0.0,
    }
    staging = evaluate_stage(Stage.PRE_STAGING, observed_v3_2)
    print(f"Staging gate v3.2: {'PASS' if staging.passed else 'FAIL'}")
    for f in staging.failed_gates:
        print(f"  - {f}")
    print()

    print("=== T+25 → T+40: rollback y v3.3 ===")
    observed_v3_3 = {
        "faithfulness": 0.93,
        "answer_correctness": 0.89,
        "context_recall": 0.87,
        "ndcg_at_5": 0.82,
        "safety_canary_leaks": 0.0,
    }
    staging_v3_3 = evaluate_stage(Stage.PRE_STAGING, observed_v3_3)
    print(f"Staging gate v3.3: {'PASS' if staging_v3_3.passed else 'FAIL'}")
    print()

    print("=== Postmortem ===")
    report = build_bug_report()
    print(f"Bug ID: {report.id}")
    print(f"Severidad: {report.severity}")
    print(f"Estado: {report.status}")
    print(f"Causa raíz: {report.root_cause[:80]}...")
    print()
    print(f"Mejoras estructurales: {len(IMPROVEMENTS)}")
    for imp in IMPROVEMENTS:
        prevents = ", ".join(imp.prevents)
        print(f"  - {imp.name} (previene {prevents})")


if __name__ == "__main__":
    main()
