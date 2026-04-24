"""
Solución del ejercicio del módulo 02.

Enunciado: Añade una quinta métrica, `noise_sensitivity`, que mida cuánto
cambia el score de faithfulness cuando se añade un chunk de ruido irrelevante
al contexto. Un buen retriever debería ser resistente al ruido.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "modules" / "02-ragas-basics"))

from src.ragas_evaluator import RAGASEvaluator


class ExtendedRAGASEvaluator(RAGASEvaluator):

    def noise_sensitivity(
        self,
        response: str,
        clean_context: list[str],
        noise_chunk: str,
    ) -> float:
        score_clean = self.faithfulness(response, clean_context)
        noisy_context = clean_context + [noise_chunk]
        score_noisy = self.faithfulness(response, noisy_context)
        sensitivity = abs(score_clean - score_noisy)
        return round(sensitivity, 3)


if __name__ == "__main__":
    evaluator = ExtendedRAGASEvaluator()
    response = "Returns are allowed within 30 days for a full refund."
    context = ["Our return policy allows returns within 30 days."]
    noise = "The capital of France is Paris and it is known for the Eiffel Tower."

    sensitivity = evaluator.noise_sensitivity(response, context, noise)
    print(f"Noise sensitivity: {sensitivity:.3f}")
    print("Interpretation: closer to 0 = more robust to noise")
