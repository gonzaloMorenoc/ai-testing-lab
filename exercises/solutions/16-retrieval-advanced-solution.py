"""Solución del ejercicio del módulo 16.

Ejercicio: decidir si activar HyDE en producción comparando NDCG@5 baseline vs
HyDE sobre un golden set. Aplica el gate canónico ΔNDCG@5 ≥ +0.05.

Modo de uso:
    python exercises/solutions/16-retrieval-advanced-solution.py
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "modules" / "16-retrieval-advanced" / "src"))
sys.path.insert(0, str(REPO))

from retrieval_evaluator import evaluate_technique  # noqa: E402
from retrieval_techniques import (  # noqa: E402
    BaselineDenseRetriever,
    Document,
    HyDERetriever,
)


def main() -> None:
    docs = [
        Document("d1", "El gato negro come pescado fresco todas las mañanas"),
        Document("d2", "Los perros corren rápido en el parque al atardecer"),
        Document("d3", "La paella valenciana lleva arroz bomba y azafrán"),
        Document("d4", "Python es un lenguaje versátil para data science"),
        Document("d5", "El gato pardo duerme en el sofá durante la tarde"),
    ]
    qrels = {
        "comida tradicional valenciana": {"d3": 2.0},
        "que come el gato": {"d1": 2.0, "d5": 0.5},
        "lenguaje para datos": {"d4": 2.0},
    }

    expansions = {
        "comida tradicional valenciana": "paella arroz bomba azafran tradicional",
        "que come el gato": "felino alimentación pescado fresco",
        "lenguaje para datos": "python data science programación",
    }

    baseline = BaselineDenseRetriever(docs)
    hyde = HyDERetriever(docs, mock_llm=lambda q: expansions.get(q, q))

    report = evaluate_technique(baseline, hyde, qrels, top_k=3)
    print(f"NDCG@5 baseline: {report.baseline_ndcg5:.3f}")
    print(f"NDCG@5 HyDE:     {report.advanced_ndcg5:.3f}")
    print(f"Δ NDCG@5:        {report.delta_ndcg:+.3f}")
    print(f"Coste extra:     {report.llm_calls_overhead:.0f} LLM call(s), "
          f"+{report.latency_overhead_ms:.0f} ms")
    print(f"HyDE justificado (gate §29.3): {report.justified}")


if __name__ == "__main__":
    main()
