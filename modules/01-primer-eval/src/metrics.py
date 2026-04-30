"""
Métricas determinísticas para CI sin llamadas LLM.

Por qué existen:
    Los tests de CI deben correr sin API keys. Estas métricas calculan scores
    heurísticos (overlap de palabras, cobertura del contexto) en vez de usar
    un LLM juez. No son equivalentes a las métricas RAGAS/DeepEval reales,
    pero demuestran la interfaz y permiten que los tests pasen de forma
    reproducible.

En los tests @pytest.mark.slow se usan las métricas reales de DeepEval.
"""

from __future__ import annotations

from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


class SimpleAnswerRelevancyMetric(BaseMetric):
    """
    Métrica determinística de relevancia: fracción de palabras del input
    que aparecen en el output (heurístico, sin LLM).
    """

    def __init__(self, threshold: float = 0.7, name: str = "SimpleAnswerRelevancy"):
        self.threshold = threshold
        self._name = name
        self.score: float = 0.0
        self.reason: str = ""

    @property
    def __name__(self) -> str:  # type: ignore[override]
        return self._name

    def measure(self, test_case: LLMTestCase, *args, **kwargs) -> float:
        query_words = {w.lower() for w in test_case.input.split() if len(w) > 3}
        output_words = {w.lower() for w in test_case.actual_output.split()}
        if not query_words:
            self.score = 1.0
            self.reason = "Empty query — trivially relevant"
            return self.score
        overlap = query_words & output_words
        self.score = round(min(1.0, len(overlap) / len(query_words) * 2), 3)
        self.reason = (
            f"{len(overlap)}/{len(query_words)} query terms found in response "
            f"(heuristic, not LLM-based)"
        )
        return self.score

    async def a_measure(self, test_case: LLMTestCase, *args, **kwargs) -> float:
        return self.measure(test_case)

    def is_successful(self) -> bool:
        return self.score >= self.threshold


class SimpleFaithfulnessMetric(BaseMetric):
    """
    Métrica determinística de fidelidad: fracción del output cubierta
    por el contexto recuperado (heurístico, sin LLM).
    """

    def __init__(self, threshold: float = 0.8, name: str = "SimpleFaithfulness"):
        self.threshold = threshold
        self._name = name
        self.score: float = 0.0
        self.reason: str = ""

    @property
    def __name__(self) -> str:  # type: ignore[override]
        return self._name

    def measure(self, test_case: LLMTestCase, *args, **kwargs) -> float:
        if not test_case.retrieval_context:
            self.score = 0.0
            self.reason = "No retrieval context provided"
            return self.score

        combined_context = " ".join(test_case.retrieval_context).lower()
        output_words = [w.lower() for w in test_case.actual_output.split() if len(w) > 4]
        if not output_words:
            self.score = 1.0
            self.reason = "Empty output — trivially faithful"
            return self.score

        supported = sum(1 for w in output_words if w in combined_context)
        self.score = round(supported / len(output_words), 3)
        self.reason = (
            f"{supported}/{len(output_words)} output words found in context "
            f"(heuristic, not LLM-based)"
        )
        return self.score

    async def a_measure(self, test_case: LLMTestCase, *args, **kwargs) -> float:
        return self.measure(test_case)

    def is_successful(self) -> bool:
        return self.score >= self.threshold
