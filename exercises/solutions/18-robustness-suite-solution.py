"""Solución del ejercicio del módulo 18.

Ejercicio: dada una lista de queries de producción, aplicar la batería completa
de perturbaciones y reportar consistency_score por categoría. Identificar
qué perturbaciones rompen más el sistema.

Modo de uso:
    python exercises/solutions/18-robustness-suite-solution.py
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "modules" / "18-robustness-suite" / "src"))
sys.path.insert(0, str(REPO))

from robustness_metrics import aggregate_by_segment  # noqa: E402
from robustness_runner import RobustnessRunner  # noqa: E402


def my_chatbot(query: str) -> str:
    """Mock determinista: responde según palabra clave."""
    q = query.lower()
    if "devolución" in q or "devoluci" in q or "devolucion" in q:
        return "Las devoluciones se aceptan en 30 días con factura."
    if "envío" in q or "envio" in q:
        return "Ofrecemos envío estándar y express."
    return "Lo siento, no entendí la consulta."


def main() -> None:
    queries = [
        "¿Cuál es la política de devoluciones?",
        "¿Qué tipos de envío están disponibles?",
        "¿Puedo cancelar mi pedido?",
        "¿Cuánto tarda el envío?",
    ]

    runner = RobustnessRunner(chatbot_answer=my_chatbot, consistency_target=0.70)
    report = runner.run(queries)

    print("=== Robustness report ===")
    print(f"Total perturbaciones: {report.n_perturbations}")
    print(f"Consistency score:  {report.consistency_score:.3f}")
    print(f"Semantic stability: {report.semantic_stability:.3f}")
    print(f"Refusal stability:  {report.refusal_stability:.3f}")
    print(f"Pasa gate:          {report.passed}")
    print()

    # Re-ejecutar para obtener resultados raw y agregar por categoría
    import random
    from perturbations import PERTURBERS  # noqa: PLC0415
    from robustness_metrics import PerturbationResult, _bow_similarity  # noqa: PLC0415

    rng = random.Random(42)
    results = []
    for q in queries:
        base = my_chatbot(q)
        for name, fn in PERTURBERS.items():
            perturbed = fn(q, rng)
            results.append(
                PerturbationResult(
                    original_query=q,
                    perturbed_query=perturbed,
                    perturbation_name=name,
                    similarity=_bow_similarity(base, my_chatbot(perturbed)),
                    refusal_changed=False,
                )
            )

    by_pert = aggregate_by_segment(results, segment_key=lambda r: r.perturbation_name)
    print("=== Por perturbación (consistency) ===")
    for name, score in sorted(by_pert.items(), key=lambda x: x[1]):
        flag = "❌" if score < 0.70 else "✓"
        print(f"  {flag} {name:25s} {score:.3f}")


if __name__ == "__main__":
    main()
