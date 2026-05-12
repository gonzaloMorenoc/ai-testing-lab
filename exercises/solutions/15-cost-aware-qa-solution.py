"""Solución del ejercicio del módulo 15.

Ejercicio: dado un baseline y un candidato, decidir si el cambio a un modelo
más caro está justificado. Criterios:
- Δ cost_usd_mean ≤ +20 % (Tabla 27.2 del manual)
- P95 latencia ≤ 2 s (Tabla 4.2)
- ROI cualitativo: documentado como argumento de negocio

Modo de uso:
    python exercises/solutions/15-cost-aware-qa-solution.py
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "modules" / "15-cost-aware-qa" / "src"))
sys.path.insert(0, str(REPO))

from cost_metrics import QueryRecord, compute_cost_latency_metrics  # noqa: E402
from cost_regression import ChangeType, CostRegressionChecker  # noqa: E402


def main() -> None:
    baseline_records = [
        QueryRecord("gpt-4o-mini", 500, 200, 800, cost_usd=0.000195) for _ in range(50)
    ]
    candidate_records = [
        QueryRecord("claude-sonnet-4-5", 500, 200, 1200, cost_usd=0.0045) for _ in range(50)
    ]

    baseline = compute_cost_latency_metrics(baseline_records)
    candidate = compute_cost_latency_metrics(candidate_records)

    checker = CostRegressionChecker()
    result = checker.check(baseline, candidate, ChangeType.MODEL_MORE_EXPENSIVE)

    print(f"Δ cost_usd_mean: {(candidate.cost_usd_mean / baseline.cost_usd_mean - 1) * 100:.1f} %")
    print(f"P95 latencia: {candidate.latency_p95_ms:.0f} ms")
    print(f"Cambio justificado: {result.passed}")
    if not result.passed:
        for v in result.violations:
            print(f"  - {v.metric}: Δ {v.delta_pct*100:.1f}% > umbral {v.threshold_pct*100:.0f}%")


if __name__ == "__main__":
    main()
