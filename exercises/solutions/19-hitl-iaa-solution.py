"""Solución del ejercicio del módulo 19.

Ejercicio: tres anotadores etiquetan 30 ejemplos (clasificación binaria).
Calcular Cohen κ pairwise, Fleiss κ y Krippendorff α. Decidir si el dataset
puede usarse como gate de release.

Modo de uso:
    python exercises/solutions/19-hitl-iaa-solution.py
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "modules" / "19-hitl-iaa" / "src"))
sys.path.insert(0, str(REPO))

from iaa_metrics import (  # noqa: E402
    HIGH_RISK_KAPPA,
    MIN_ACCEPTABLE_KAPPA,
    cohen_kappa,
    fleiss_kappa,
    krippendorff_alpha_nominal,
)


def main() -> None:
    # 30 ítems, 3 anotadores. Acuerdo alto pero no perfecto.
    annotator_a = (["yes"] * 12 + ["no"] * 18)
    annotator_b = (["yes"] * 11 + ["no"] * 1 + ["no"] * 17 + ["yes"] * 1)
    annotator_c = (["yes"] * 12 + ["no"] * 17 + ["yes"] * 1)
    annotations = list(zip(annotator_a, annotator_b, annotator_c, strict=True))

    print("=== Pairwise Cohen κ ===")
    print(f"  A vs B: {cohen_kappa(annotator_a, annotator_b).value:.3f}")
    print(f"  A vs C: {cohen_kappa(annotator_a, annotator_c).value:.3f}")
    print(f"  B vs C: {cohen_kappa(annotator_b, annotator_c).value:.3f}")
    print()

    fleiss = fleiss_kappa([list(row) for row in annotations])
    print(f"Fleiss κ: {fleiss.value:.3f} ({fleiss.interpretation})")

    alpha = krippendorff_alpha_nominal([list(row) for row in annotations])
    print(f"Krippendorff α: {alpha.value:.3f} ({alpha.interpretation})")
    print()

    # Decisión de release
    print(f"Umbral mínimo aceptable: {MIN_ACCEPTABLE_KAPPA}")
    print(f"Umbral alto riesgo:      {HIGH_RISK_KAPPA}")
    print()
    if alpha.value >= HIGH_RISK_KAPPA:
        print("✓ Dataset apto para gate en dominio regulado.")
    elif alpha.value >= MIN_ACCEPTABLE_KAPPA:
        print("✓ Dataset apto para gate estándar. NO suficiente para alto riesgo.")
    else:
        print("❌ Recalibrar guidelines y re-anotar.")


if __name__ == "__main__":
    main()
