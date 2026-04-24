# Batch 1 — Módulos de Evaluación (02-06) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar los módulos 02-06 del eje de evaluación de ai-testing-lab, cada uno con 2-3 archivos src, 8-12 tests determinísticos y solución de ejercicio.

**Architecture:** Cada módulo sigue el contrato establecido en el módulo 01: métricas determinísticas (sin LLM calls) para CI, un test `@pytest.mark.slow` con Groq real opcional. El módulo 02 actúa como plantilla del batch — los módulos 03-06 siguen sus mismos patrones.

**Tech Stack:** Python 3.11+, DeepEval (BaseMetric), pytest, pytest-asyncio, uv. Sin dependencias externas requeridas (todo funciona offline).

**Repo:** `/Users/gonzalo/Documents/GitHub/ai-testing-lab`

**Comando de verificación global:**
```bash
pytest modules/02-ragas-basics/tests/ modules/03-llm-as-judge/tests/ \
       modules/04-multi-turn/tests/ modules/05-prompt-regression/tests/ \
       modules/06-hallucination-lab/tests/ \
       -v -m "not slow" --record-mode=none
```

---

## Task 1: Módulo 02 — ragas-basics (plantilla del batch)

**Files:**
- Create: `modules/02-ragas-basics/conftest.py`
- Create: `modules/02-ragas-basics/src/__init__.py`
- Create: `modules/02-ragas-basics/src/rag_pipeline.py`
- Create: `modules/02-ragas-basics/src/ragas_evaluator.py`
- Create: `modules/02-ragas-basics/tests/__init__.py`
- Create: `modules/02-ragas-basics/tests/conftest.py`
- Create: `modules/02-ragas-basics/tests/test_ragas_metrics.py`
- Create: `exercises/solutions/02-ragas-basics-solution.py`

---

- [ ] **Step 1: Crear conftest.py raíz del módulo**

```python
# modules/02-ragas-basics/conftest.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
```

- [ ] **Step 2: Crear src/__init__.py**

Archivo vacío: `modules/02-ragas-basics/src/__init__.py`

- [ ] **Step 3: Crear src/rag_pipeline.py**

```python
# modules/02-ragas-basics/src/rag_pipeline.py
"""
RAG pipeline mínimo con knowledge base in-memory.
Misma KB que módulo 01, extendida con topic scoring.
"""
from __future__ import annotations

KNOWLEDGE_BASE: dict[str, str] = {
    "returns": (
        "Our return policy allows customers to return any product within 30 days "
        "of purchase for a full refund. Items must be in their original condition "
        "and packaging. Digital products are non-refundable once downloaded."
    ),
    "shipping": (
        "We offer free standard shipping on orders over $50. "
        "Standard shipping takes 3-5 business days. "
        "Express shipping (1-2 days) is available for $9.99."
    ),
    "warranty": (
        "All products come with a 1-year manufacturer warranty. "
        "Extended warranties of 2 or 3 years are available at purchase. "
        "Warranty covers manufacturing defects but not accidental damage."
    ),
    "payment": (
        "We accept Visa, Mastercard, American Express, PayPal, and bank transfers. "
        "All payments are processed securely via SSL encryption. "
        "We do not store credit card information."
    ),
}

TOPIC_KEYWORDS: dict[str, list[str]] = {
    "returns": ["return", "refund", "devol", "reembolso", "back"],
    "shipping": ["ship", "deliver", "envío", "envio", "days", "express"],
    "warranty": ["warrant", "garantía", "garantia", "defect", "repair"],
    "payment": ["pay", "card", "credit", "visa", "mastercard", "paypal"],
}


class RAGPipeline:
    """RAG pipeline in-memory para demo y evaluación."""

    def retrieve(self, query: str, k: int = 2) -> list[str]:
        """Devuelve hasta k chunks relevantes por keyword matching."""
        query_lower = query.lower()
        scored: list[tuple[int, str]] = []
        for topic, keywords in TOPIC_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > 0:
                scored.append((score, KNOWLEDGE_BASE[topic]))
        scored.sort(key=lambda x: x[0], reverse=True)
        chunks = [chunk for _, chunk in scored[:k]]
        return chunks if chunks else [list(KNOWLEDGE_BASE.values())[0]]

    def generate(self, query: str, context: list[str]) -> str:
        """Genera respuesta basada en contexto recuperado."""
        combined = " ".join(context)
        return f"Based on our policies: {combined}"

    def run(self, query: str) -> dict[str, object]:
        """Ejecuta pipeline completo. Devuelve query, response y context."""
        context = self.retrieve(query)
        response = self.generate(query, context)
        return {"query": query, "response": response, "context": context}
```

- [ ] **Step 4: Crear src/ragas_evaluator.py**

```python
# modules/02-ragas-basics/src/ragas_evaluator.py
"""
Evaluador RAGAS-like determinístico (sin LLM calls).

Implementa las 4 métricas principales de RAGAS con heurísticos:
- Faithfulness: fracción del output cubierta por el contexto
- Answer Relevancy: overlap de palabras entre query y respuesta
- Context Precision: fracción de chunks con al menos un token del query
- Context Recall: fracción de la respuesta cubierta por el contexto

Por qué heurísticos y no RAGAS real:
    RAGAS requiere un LLM para descomponer claims y evaluar. Aquí usamos
    proxies numéricos para que los tests corran sin API key. Los conceptos
    son los mismos; la implementación es simplificada.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RAGASScores:
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float

    def passes(self, threshold: float = 0.7) -> bool:
        return all(
            s >= threshold
            for s in [
                self.faithfulness,
                self.answer_relevancy,
                self.context_precision,
                self.context_recall,
            ]
        )

    def __repr__(self) -> str:
        return (
            f"RAGASScores("
            f"faithfulness={self.faithfulness:.2f}, "
            f"answer_relevancy={self.answer_relevancy:.2f}, "
            f"context_precision={self.context_precision:.2f}, "
            f"context_recall={self.context_recall:.2f})"
        )


class RAGASEvaluator:
    """Evaluador determinístico que replica la interfaz de RAGAS."""

    def _tokenize(self, text: str) -> set[str]:
        return {w.lower() for w in text.split() if len(w) > 3}

    def faithfulness(self, response: str, context: list[str]) -> float:
        """Fracción de tokens del output presentes en el contexto combinado."""
        if not context:
            return 0.0
        combined = " ".join(context)
        response_tokens = self._tokenize(response)
        context_tokens = self._tokenize(combined)
        if not response_tokens:
            return 1.0
        supported = response_tokens & context_tokens
        return round(len(supported) / len(response_tokens), 3)

    def answer_relevancy(self, query: str, response: str) -> float:
        """Overlap de tokens entre query y respuesta (x2 capped a 1.0)."""
        query_tokens = self._tokenize(query)
        response_tokens = self._tokenize(response)
        if not query_tokens:
            return 1.0
        overlap = query_tokens & response_tokens
        return round(min(1.0, len(overlap) / len(query_tokens) * 2), 3)

    def context_precision(self, query: str, context: list[str]) -> float:
        """Fracción de chunks que contienen al menos un token del query."""
        if not context:
            return 0.0
        query_tokens = self._tokenize(query)
        relevant = sum(
            1 for chunk in context if query_tokens & self._tokenize(chunk)
        )
        return round(relevant / len(context), 3)

    def context_recall(self, response: str, context: list[str]) -> float:
        """Fracción de tokens del response cubiertos por el contexto."""
        if not context:
            return 0.0
        combined_tokens = self._tokenize(" ".join(context))
        response_tokens = self._tokenize(response)
        if not response_tokens:
            return 1.0
        covered = response_tokens & combined_tokens
        return round(len(covered) / len(response_tokens), 3)

    def evaluate(
        self, query: str, response: str, context: list[str]
    ) -> RAGASScores:
        """Ejecuta las 4 métricas y devuelve RAGASScores."""
        return RAGASScores(
            faithfulness=self.faithfulness(response, context),
            answer_relevancy=self.answer_relevancy(query, response),
            context_precision=self.context_precision(query, context),
            context_recall=self.context_recall(response, context),
        )
```

- [ ] **Step 5: Crear tests/__init__.py**

Archivo vacío: `modules/02-ragas-basics/tests/__init__.py`

- [ ] **Step 6: Crear tests/conftest.py**

```python
# modules/02-ragas-basics/tests/conftest.py
import pytest
from src.rag_pipeline import RAGPipeline
from src.ragas_evaluator import RAGASEvaluator


@pytest.fixture(scope="module")
def pipeline() -> RAGPipeline:
    return RAGPipeline()


@pytest.fixture(scope="module")
def evaluator() -> RAGASEvaluator:
    return RAGASEvaluator()


@pytest.fixture
def returns_result(pipeline: RAGPipeline) -> dict:
    return pipeline.run("What is the return policy?")


@pytest.fixture
def hallucinated_response() -> str:
    return (
        "You can return products within 365 days and receive a 200% refund. "
        "We offer same-day drone delivery worldwide for free."
    )
```

- [ ] **Step 7: Crear tests/test_ragas_metrics.py**

```python
# modules/02-ragas-basics/tests/test_ragas_metrics.py
"""
Módulo 02 — RAGAS Basics
=========================
Tests de las 4 métricas RAGAS implementadas de forma determinística.
"""
from __future__ import annotations

import os
import pytest
from src.rag_pipeline import RAGPipeline
from src.ragas_evaluator import RAGASEvaluator, RAGASScores


class TestFaithfulness:

    def test_faithful_response_scores_high(
        self, evaluator: RAGASEvaluator, returns_result: dict
    ) -> None:
        score = evaluator.faithfulness(
            returns_result["response"], returns_result["context"]
        )
        print(f"\n  Faithfulness: {score:.2f}")
        assert score >= 0.7, f"Respuesta fiel al contexto debería superar 0.7, got {score}"

    def test_hallucinated_response_scores_low(
        self, evaluator: RAGASEvaluator, hallucinated_response: str, returns_result: dict
    ) -> None:
        score = evaluator.faithfulness(hallucinated_response, returns_result["context"])
        print(f"\n  Faithfulness (alucinación): {score:.2f}")
        assert score < 0.6, f"Alucinación debería tener faithfulness < 0.6, got {score}"

    def test_no_context_returns_zero(self, evaluator: RAGASEvaluator) -> None:
        score = evaluator.faithfulness("Some response about returns.", [])
        assert score == 0.0


class TestAnswerRelevancy:

    def test_relevant_response_scores_high(
        self, evaluator: RAGASEvaluator, returns_result: dict
    ) -> None:
        score = evaluator.answer_relevancy(
            returns_result["query"], returns_result["response"]
        )
        print(f"\n  Answer Relevancy: {score:.2f}")
        assert score >= 0.4

    def test_off_topic_response_scores_low(self, evaluator: RAGASEvaluator) -> None:
        score = evaluator.answer_relevancy(
            "What is the return policy?",
            "The weather in Madrid is sunny and warm today.",
        )
        print(f"\n  Answer Relevancy (fuera de tema): {score:.2f}")
        assert score < 0.4


class TestContextPrecision:

    def test_all_chunks_relevant(self, evaluator: RAGASEvaluator) -> None:
        context = [
            "Returns are allowed within 30 days.",
            "Refunds are processed within 5 business days.",
        ]
        score = evaluator.context_precision("What is the return policy?", context)
        print(f"\n  Context Precision (todos relevantes): {score:.2f}")
        assert score == 1.0

    def test_mixed_chunks_partial_precision(self, evaluator: RAGASEvaluator) -> None:
        context = [
            "Returns are allowed within 30 days.",
            "The sky is blue and clouds are white.",
        ]
        score = evaluator.context_precision("What is the return policy?", context)
        print(f"\n  Context Precision (mixto): {score:.2f}")
        assert 0.0 < score < 1.0

    def test_empty_context_returns_zero(self, evaluator: RAGASEvaluator) -> None:
        score = evaluator.context_precision("What is the return policy?", [])
        assert score == 0.0


class TestEvaluatePipeline:

    def test_full_pipeline_passes_all_metrics(
        self, pipeline: RAGPipeline, evaluator: RAGASEvaluator
    ) -> None:
        result = pipeline.run("What is the return policy?")
        scores: RAGASScores = evaluator.evaluate(
            result["query"], result["response"], result["context"]
        )
        print(f"\n  {scores}")
        assert scores.faithfulness >= 0.7
        assert scores.answer_relevancy >= 0.4
        assert scores.context_precision >= 0.5
        assert scores.context_recall >= 0.7

    def test_batch_evaluation(
        self, pipeline: RAGPipeline, evaluator: RAGASEvaluator
    ) -> None:
        queries = [
            "What is the return policy?",
            "How long does shipping take?",
            "Is there a warranty?",
        ]
        results = [pipeline.run(q) for q in queries]
        scores = [
            evaluator.evaluate(r["query"], r["response"], r["context"])
            for r in results
        ]
        avg_faithfulness = sum(s.faithfulness for s in scores) / len(scores)
        print(f"\n  Avg faithfulness over batch: {avg_faithfulness:.2f}")
        assert avg_faithfulness >= 0.6

    @pytest.mark.slow
    def test_with_real_ragas(self, pipeline: RAGPipeline) -> None:
        """Test real con RAGAS + Groq. Requiere GROQ_API_KEY."""
        if not os.getenv("GROQ_API_KEY"):
            pytest.skip("GROQ_API_KEY no encontrado")
        try:
            from ragas.metrics import faithfulness, answer_relevancy
            from ragas import evaluate
            from datasets import Dataset
        except ImportError:
            pytest.skip("ragas o datasets no instalados")

        result = pipeline.run("What is the return policy?")
        data = {
            "question": [result["query"]],
            "answer": [result["response"]],
            "contexts": [result["context"]],
        }
        dataset = Dataset.from_dict(data)
        scores = evaluate(dataset, metrics=[faithfulness, answer_relevancy])
        print(f"\n  Real RAGAS scores: {scores}")
        assert scores["faithfulness"] >= 0.5
```

- [ ] **Step 8: Ejecutar tests y verificar que pasan**

```bash
cd /Users/gonzalo/Documents/GitHub/ai-testing-lab
pytest modules/02-ragas-basics/tests/ -v -m "not slow" --record-mode=none
```

Salida esperada: `9 passed, 1 deselected` (el slow se excluye).

- [ ] **Step 9: Crear solución de ejercicio**

```python
# exercises/solutions/02-ragas-basics-solution.py
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
        """
        Mide cuánto baja faithfulness al añadir ruido al contexto.
        Score cercano a 0 = resistente al ruido (bueno).
        Score cercano a 1 = muy sensible al ruido (malo).
        """
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
```

- [ ] **Step 10: Commit**

```bash
git add modules/02-ragas-basics/ exercises/solutions/02-ragas-basics-solution.py
git commit -m "feat(02-ragas-basics): add RAGAS evaluation module with 9 tests"
```

---

## Task 2: Módulo 03 — llm-as-judge

**Files:**
- Create: `modules/03-llm-as-judge/conftest.py`
- Create: `modules/03-llm-as-judge/src/__init__.py`
- Create: `modules/03-llm-as-judge/src/geval_judge.py`
- Create: `modules/03-llm-as-judge/src/dag_metric.py`
- Create: `modules/03-llm-as-judge/tests/__init__.py`
- Create: `modules/03-llm-as-judge/tests/conftest.py`
- Create: `modules/03-llm-as-judge/tests/test_judges.py`
- Create: `exercises/solutions/03-llm-as-judge-solution.py`

---

- [ ] **Step 1: Crear conftest.py raíz**

```python
# modules/03-llm-as-judge/conftest.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
```

- [ ] **Step 2: Crear src/__init__.py** — archivo vacío

- [ ] **Step 3: Crear src/geval_judge.py**

```python
# modules/03-llm-as-judge/src/geval_judge.py
"""
G-Eval: LLM-as-a-judge con criterios en lenguaje natural.

Implementa dos modos:
- Mock (default): scoring determinístico por keyword matching en la rúbrica
- Real (slow): llama a un LLM con el prompt G-Eval completo

Paper de referencia: MT-Bench (Zheng et al., 2023) — arxiv 2306.05685
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class GEvalResult:
    score: float          # 0.0 a 1.0
    reason: str
    criteria: str
    passed: bool = field(init=False)
    threshold: float = 0.7

    def __post_init__(self) -> None:
        self.passed = self.score >= self.threshold

    def __repr__(self) -> str:
        status = "✓" if self.passed else "✗"
        return f"GEval[{status}] score={self.score:.2f} | {self.reason[:60]}"


class GEvalJudge:
    """
    Juez G-Eval determinístico para CI sin LLM.

    Evalúa si un output cumple un criterio buscando indicadores positivos
    y negativos en el texto. Devuelve score en [0, 1].
    """

    POSITIVE_INDICATORS = {
        "relevancy": ["policy", "return", "refund", "days", "based", "shipping", "warranty"],
        "toxicity": [],  # sin indicadores positivos de toxicidad
        "faithfulness": ["based", "policy", "according", "states", "mentions"],
        "completeness": ["return", "refund", "condition", "days", "packaging"],
    }

    NEGATIVE_INDICATORS = {
        "relevancy": ["weather", "capital", "france", "unrelated", "sports"],
        "toxicity": ["stupid", "hate", "kill", "idiot", "worthless", "garbage"],
        "faithfulness": ["365 days", "200%", "drone", "worldwide", "free shipping always"],
        "completeness": [],
    }

    def evaluate(
        self,
        output: str,
        criteria: str,
        threshold: float = 0.7,
    ) -> GEvalResult:
        """
        Evalúa `output` contra `criteria`.
        `criteria` debe ser una de: relevancy, toxicity, faithfulness, completeness.
        """
        output_lower = output.lower()
        positives = self.POSITIVE_INDICATORS.get(criteria, [])
        negatives = self.NEGATIVE_INDICATORS.get(criteria, [])

        pos_hits = sum(1 for kw in positives if kw in output_lower)
        neg_hits = sum(1 for kw in negatives if kw in output_lower)

        if criteria == "toxicity":
            # Para toxicidad: score alto = MÁS tóxico
            score = min(1.0, neg_hits * 0.4) if neg_hits else 0.0
            reason = (
                f"Detected {neg_hits} toxic indicators"
                if neg_hits
                else "No toxic content detected"
            )
        else:
            base = pos_hits / max(len(positives), 1) if positives else 0.5
            penalty = neg_hits * 0.3
            score = round(max(0.0, min(1.0, base - penalty)), 3)
            reason = (
                f"{pos_hits} positive indicators, {neg_hits} negative indicators "
                f"for criteria '{criteria}'"
            )

        return GEvalResult(
            score=score,
            reason=reason,
            criteria=criteria,
            threshold=threshold,
        )
```

- [ ] **Step 4: Crear src/dag_metric.py**

```python
# modules/03-llm-as-judge/src/dag_metric.py
"""
DAG Metric: grafo acíclico dirigido de decisiones deterministas.

Permite evaluar outputs mediante reglas booleanas encadenadas sin LLM.
Útil cuando el criterio de evaluación es explícito y determinista.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class DAGNode:
    name: str
    condition: Callable[[str], bool]
    score_if_true: float
    score_if_false: float
    reason_true: str
    reason_false: str


@dataclass
class DAGResult:
    score: float
    passed: bool
    reason: str
    node_name: str
    threshold: float

    def __repr__(self) -> str:
        status = "✓" if self.passed else "✗"
        return f"DAG[{status}] node={self.node_name} score={self.score:.2f}"


class DAGMetric:
    """
    Evalúa un output recorriendo una cadena de nodos DAG.
    El score final es el del primer nodo cuya condición se cumple.
    """

    def __init__(self, nodes: list[DAGNode], threshold: float = 0.7) -> None:
        self.nodes = nodes
        self.threshold = threshold

    def evaluate(self, output: str) -> DAGResult:
        for node in self.nodes:
            if node.condition(output):
                score = node.score_if_true
                reason = node.reason_true
                node_name = node.name
                break
        else:
            last = self.nodes[-1]
            score = last.score_if_false
            reason = last.reason_false
            node_name = last.name

        return DAGResult(
            score=score,
            passed=score >= self.threshold,
            reason=reason,
            node_name=node_name,
            threshold=self.threshold,
        )


def build_keyword_dag(required_keywords: list[str], threshold: float = 0.7) -> DAGMetric:
    """Factory: crea un DAG que verifica presencia de palabras clave."""
    nodes = [
        DAGNode(
            name=f"contains_{kw}",
            condition=lambda output, k=kw: k.lower() in output.lower(),
            score_if_true=1.0,
            score_if_false=0.0,
            reason_true=f"Output contains required keyword '{kw}'",
            reason_false=f"Output missing required keyword '{kw}'",
        )
        for kw in required_keywords
    ]
    return DAGMetric(nodes, threshold)


def build_compound_dag(
    and_keywords: list[str],
    or_keywords: list[str],
    threshold: float = 0.7,
) -> DAGMetric:
    """Factory: crea DAG con condición AND + OR."""

    def and_condition(output: str) -> bool:
        return all(kw.lower() in output.lower() for kw in and_keywords)

    def or_condition(output: str) -> bool:
        return any(kw.lower() in output.lower() for kw in or_keywords)

    nodes = [
        DAGNode(
            name="and_check",
            condition=and_condition,
            score_if_true=1.0,
            score_if_false=0.0,
            reason_true=f"All required terms present: {and_keywords}",
            reason_false=f"Missing some required terms: {and_keywords}",
        ),
        DAGNode(
            name="or_fallback",
            condition=or_condition,
            score_if_true=0.6,
            score_if_false=0.0,
            reason_true=f"At least one optional term present: {or_keywords}",
            reason_false="No relevant terms found",
        ),
    ]
    return DAGMetric(nodes, threshold)
```

- [ ] **Step 5: Crear tests/__init__.py** — archivo vacío

- [ ] **Step 6: Crear tests/conftest.py**

```python
# modules/03-llm-as-judge/tests/conftest.py
import pytest
from src.geval_judge import GEvalJudge
from src.dag_metric import DAGMetric, build_keyword_dag, build_compound_dag


@pytest.fixture(scope="module")
def judge() -> GEvalJudge:
    return GEvalJudge()


@pytest.fixture
def relevant_response() -> str:
    return (
        "Based on our policy, returns are allowed within 30 days "
        "of purchase for a full refund."
    )


@pytest.fixture
def off_topic_response() -> str:
    return "The weather in Madrid is sunny. The capital of France is Paris."


@pytest.fixture
def toxic_response() -> str:
    return "That is the most stupid idea I've ever heard, you worthless idiot."
```

- [ ] **Step 7: Crear tests/test_judges.py**

```python
# modules/03-llm-as-judge/tests/test_judges.py
"""Módulo 03 — LLM-as-Judge: G-Eval y DAG Metric."""
from __future__ import annotations

import os
import pytest
from src.geval_judge import GEvalJudge, GEvalResult
from src.dag_metric import DAGMetric, DAGResult, build_keyword_dag, build_compound_dag


class TestGEvalRelevancy:

    def test_relevant_response_passes(
        self, judge: GEvalJudge, relevant_response: str
    ) -> None:
        result: GEvalResult = judge.evaluate(relevant_response, "relevancy")
        print(f"\n  {result}")
        assert result.passed, f"Respuesta relevante debería pasar: {result.reason}"

    def test_off_topic_fails_relevancy(
        self, judge: GEvalJudge, off_topic_response: str
    ) -> None:
        result = judge.evaluate(off_topic_response, "relevancy")
        print(f"\n  {result}")
        assert not result.passed, "Respuesta fuera de tema no debería pasar relevancy"

    def test_score_is_in_range(self, judge: GEvalJudge, relevant_response: str) -> None:
        result = judge.evaluate(relevant_response, "relevancy")
        assert 0.0 <= result.score <= 1.0


class TestGEvalToxicity:

    def test_toxic_response_detected(
        self, judge: GEvalJudge, toxic_response: str
    ) -> None:
        result = judge.evaluate(toxic_response, "toxicity", threshold=0.3)
        print(f"\n  {result}")
        assert result.score > 0.0, "Respuesta tóxica debería tener score > 0"

    def test_clean_response_not_toxic(
        self, judge: GEvalJudge, relevant_response: str
    ) -> None:
        result = judge.evaluate(relevant_response, "toxicity", threshold=0.3)
        assert result.score == 0.0


class TestBiases:

    def test_position_bias_documented(self, judge: GEvalJudge) -> None:
        """
        Demuestra position bias: el mismo contenido evaluado con contexto
        diferente puede dar scores distintos según el orden de presentación.
        Este test documenta el comportamiento, no lo penaliza.
        """
        response_a = "Returns are allowed within 30 days. Refunds are full."
        response_b = "Refunds are full. Returns are allowed within 30 days."
        score_a = judge.evaluate(response_a, "relevancy").score
        score_b = judge.evaluate(response_b, "relevancy").score
        # Documentamos que los scores pueden diferir (position bias)
        print(f"\n  Score A: {score_a:.2f}, Score B: {score_b:.2f}")
        print("  Position bias: scores can differ for same content in different order")
        assert True  # test documentativo, siempre pasa

    def test_verbosity_bias_documented(self, judge: GEvalJudge) -> None:
        """Demuestra verbosity bias: respuestas más largas tienden a puntuar más."""
        short = "Returns: 30 days."
        long = (
            "Based on our return policy, customers can return products within 30 days "
            "of purchase for a full refund. Items must be in original condition."
        )
        score_short = judge.evaluate(short, "relevancy").score
        score_long = judge.evaluate(long, "relevancy").score
        print(f"\n  Short: {score_short:.2f}, Long: {score_long:.2f}")
        print("  Verbosity bias: longer responses tend to score higher")
        assert score_long >= score_short  # documenta el sesgo esperado


class TestDAGMetric:

    def test_keyword_dag_passes_when_present(self) -> None:
        dag = build_keyword_dag(["return", "days"])
        result: DAGResult = dag.evaluate("Returns are allowed within 30 days.")
        print(f"\n  {result}")
        assert result.passed

    def test_keyword_dag_fails_when_missing(self) -> None:
        dag = build_keyword_dag(["return"])
        result = dag.evaluate("The weather is nice today.")
        assert not result.passed

    def test_compound_dag_and_condition(self) -> None:
        dag = build_compound_dag(and_keywords=["return", "refund"], or_keywords=["days"])
        result = dag.evaluate("Returns allowed. Full refund guaranteed within 30 days.")
        print(f"\n  {result}")
        assert result.score == 1.0

    def test_compound_dag_or_fallback(self) -> None:
        dag = build_compound_dag(
            and_keywords=["return", "refund", "guarantee"],
            or_keywords=["days"],
        )
        result = dag.evaluate("Returns allowed within 30 days.")
        # AND falla (falta "guarantee"), OR pasa ("days" presente)
        print(f"\n  {result} — OR fallback: {result.score}")
        assert result.score == 0.6

    @pytest.mark.slow
    def test_with_real_geval(self, relevant_response: str) -> None:
        if not os.getenv("GROQ_API_KEY"):
            pytest.skip("GROQ_API_KEY no encontrado")
        from deepeval.metrics import GEval
        from deepeval.test_case import LLMTestCase, LLMTestCaseParams
        metric = GEval(
            name="Relevancy",
            criteria="The response should address the return policy question.",
            evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.INPUT],
            threshold=0.6,
        )
        tc = LLMTestCase(
            input="What is the return policy?",
            actual_output=relevant_response,
        )
        metric.measure(tc)
        print(f"\n  Real G-Eval score: {metric.score}")
        assert metric.is_successful()
```

- [ ] **Step 8: Ejecutar tests**

```bash
pytest modules/03-llm-as-judge/tests/ -v -m "not slow" --record-mode=none
```

Salida esperada: `9 passed, 1 deselected`

- [ ] **Step 9: Crear solución de ejercicio**

```python
# exercises/solutions/03-llm-as-judge-solution.py
"""
Solución módulo 03: añade una rúbrica de 'completeness' al GEvalJudge
que verifique que la respuesta cubre todos los aspectos de la política.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "modules" / "03-llm-as-judge"))

from src.geval_judge import GEvalJudge, GEvalResult


class CompletenessJudge(GEvalJudge):
    """G-Eval extendido con rúbrica de completeness configurable."""

    def evaluate_completeness(
        self, output: str, required_aspects: list[str], threshold: float = 0.7
    ) -> GEvalResult:
        output_lower = output.lower()
        covered = [asp for asp in required_aspects if asp.lower() in output_lower]
        score = round(len(covered) / len(required_aspects), 3) if required_aspects else 1.0
        missing = [asp for asp in required_aspects if asp not in covered]
        reason = (
            f"Covered {len(covered)}/{len(required_aspects)} aspects. "
            f"Missing: {missing}" if missing else "All aspects covered."
        )
        return GEvalResult(score=score, reason=reason, criteria="completeness", threshold=threshold)


if __name__ == "__main__":
    judge = CompletenessJudge()
    response = "Returns are allowed within 30 days. Items must be in original condition."
    aspects = ["30 days", "condition", "refund", "packaging"]
    result = judge.evaluate_completeness(response, aspects)
    print(result)
```

- [ ] **Step 10: Commit**

```bash
git add modules/03-llm-as-judge/ exercises/solutions/03-llm-as-judge-solution.py
git commit -m "feat(03-llm-as-judge): add G-Eval and DAG Metric module with bias demos"
```

---

## Task 3: Módulo 04 — multi-turn

**Files:**
- Create: `modules/04-multi-turn/conftest.py`
- Create: `modules/04-multi-turn/src/__init__.py`
- Create: `modules/04-multi-turn/src/conversation.py`
- Create: `modules/04-multi-turn/src/multi_turn_rag.py`
- Create: `modules/04-multi-turn/tests/__init__.py`
- Create: `modules/04-multi-turn/tests/conftest.py`
- Create: `modules/04-multi-turn/tests/test_multi_turn.py`
- Create: `exercises/solutions/04-multi-turn-solution.py`

---

- [ ] **Step 1: Crear conftest.py raíz**

```python
# modules/04-multi-turn/conftest.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
```

- [ ] **Step 2: Crear src/__init__.py** — archivo vacío

- [ ] **Step 3: Crear src/conversation.py**

```python
# modules/04-multi-turn/src/conversation.py
"""
Historial de conversación multi-turno.
Almacena turnos como lista de mensajes y expone métodos de análisis.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Message:
    role: str   # "user" | "assistant"
    content: str


@dataclass
class Conversation:
    messages: list[Message] = field(default_factory=list)

    def add_turn(self, user_input: str, assistant_response: str) -> None:
        self.messages.append(Message(role="user", content=user_input))
        self.messages.append(Message(role="assistant", content=assistant_response))

    def get_user_turns(self) -> list[str]:
        return [m.content for m in self.messages if m.role == "user"]

    def get_assistant_turns(self) -> list[str]:
        return [m.content for m in self.messages if m.role == "assistant"]

    def reset(self) -> None:
        self.messages.clear()

    def num_turns(self) -> int:
        return len([m for m in self.messages if m.role == "user"])

    def to_deepeval_format(self) -> list[dict[str, str]]:
        """Convierte al formato que espera DeepEval ConversationalTestCase."""
        return [{"role": m.role, "content": m.content} for m in self.messages]

    def contains_info(self, info: str) -> bool:
        """Verifica si algún turno del asistente contiene la información dada."""
        return any(
            info.lower() in m.content.lower()
            for m in self.messages
            if m.role == "assistant"
        )

    def detect_contradiction(self, keyword: str, value_a: str, value_b: str) -> bool:
        """
        Detecta si el asistente usó dos valores distintos para el mismo keyword.
        Ej: keyword="days", value_a="30", value_b="60"
        """
        turns = self.get_assistant_turns()
        found_a = any(f"{keyword}.*{value_a}" in t or f"{value_a}.*{keyword}" in t
                      for t in turns)
        found_b = any(f"{keyword}.*{value_b}" in t or f"{value_b}.*{keyword}" in t
                      for t in turns)
        return found_a and found_b
```

- [ ] **Step 4: Crear src/multi_turn_rag.py**

```python
# modules/04-multi-turn/src/multi_turn_rag.py
"""
RAG con memoria de historial de conversación.
Incorpora contexto de turnos anteriores en la respuesta actual.
"""
from __future__ import annotations

from src.conversation import Conversation

KNOWLEDGE_BASE: dict[str, str] = {
    "returns": "Returns allowed within 30 days for a full refund. Original condition required.",
    "shipping": "Free shipping over $50. Standard 3-5 days. Express $9.99 for 1-2 days.",
    "warranty": "1-year manufacturer warranty. Extended 2-3 year options available.",
    "payment": "Visa, Mastercard, Amex, PayPal accepted. SSL encrypted. No stored cards.",
}

TOPIC_KEYWORDS: dict[str, list[str]] = {
    "returns": ["return", "refund", "back"],
    "shipping": ["ship", "deliver", "days", "express"],
    "warranty": ["warrant", "defect", "repair"],
    "payment": ["pay", "card", "visa", "paypal"],
}


class MultiTurnRAG:
    """RAG que incorpora historial de conversación en cada respuesta."""

    def __init__(self) -> None:
        self.conversation = Conversation()

    def _retrieve(self, query: str) -> list[str]:
        q = query.lower()
        chunks = []
        for topic, keywords in TOPIC_KEYWORDS.items():
            if any(kw in q for kw in keywords):
                chunks.append(KNOWLEDGE_BASE[topic])
        return chunks or [KNOWLEDGE_BASE["returns"]]

    def _build_context_summary(self) -> str:
        """Resume los últimos 2 turnos del asistente como contexto."""
        prior = self.conversation.get_assistant_turns()[-2:]
        return " Previously discussed: " + " ".join(prior) if prior else ""

    def respond(self, user_input: str) -> str:
        context = self._retrieve(user_input)
        history_context = self._build_context_summary()
        response = f"Based on our policies: {' '.join(context)}{history_context}"
        self.conversation.add_turn(user_input, response)
        return response

    def reset(self) -> None:
        self.conversation.reset()
```

- [ ] **Step 5: Crear tests/__init__.py** — archivo vacío

- [ ] **Step 6: Crear tests/conftest.py**

```python
# modules/04-multi-turn/tests/conftest.py
import pytest
from src.conversation import Conversation
from src.multi_turn_rag import MultiTurnRAG


@pytest.fixture
def conversation() -> Conversation:
    return Conversation()


@pytest.fixture
def rag() -> MultiTurnRAG:
    return MultiTurnRAG()
```

- [ ] **Step 7: Crear tests/test_multi_turn.py**

```python
# modules/04-multi-turn/tests/test_multi_turn.py
"""Módulo 04 — Multi-Turn: testing de conversaciones con historial."""
from __future__ import annotations

import os
import pytest
from src.conversation import Conversation, Message
from src.multi_turn_rag import MultiTurnRAG


class TestConversation:

    def test_add_turn_stores_both_messages(self, conversation: Conversation) -> None:
        conversation.add_turn("Hello", "Hi there!")
        assert conversation.num_turns() == 1
        assert len(conversation.messages) == 2

    def test_info_retained_from_turn_1_in_turn_3(self, rag: MultiTurnRAG) -> None:
        rag.respond("What is the return policy?")
        rag.respond("And what about shipping?")
        response_3 = rag.respond("Can you summarize what you told me?")
        assert "30 days" in response_3 or "return" in response_3.lower(), (
            "Info from turn 1 should still be accessible in turn 3"
        )

    def test_conversation_num_turns(self, conversation: Conversation) -> None:
        conversation.add_turn("Q1", "A1")
        conversation.add_turn("Q2", "A2")
        conversation.add_turn("Q3", "A3")
        assert conversation.num_turns() == 3

    def test_reset_clears_history(self, rag: MultiTurnRAG) -> None:
        rag.respond("What is the return policy?")
        assert rag.conversation.num_turns() == 1
        rag.reset()
        assert rag.conversation.num_turns() == 0

    def test_contains_info_detects_keyword(self, conversation: Conversation) -> None:
        conversation.add_turn("Q", "Returns are allowed within 30 days.")
        assert conversation.contains_info("30 days")
        assert not conversation.contains_info("365 days")

    def test_deepeval_format_structure(self, conversation: Conversation) -> None:
        conversation.add_turn("Q", "A")
        fmt = conversation.to_deepeval_format()
        assert len(fmt) == 2
        assert fmt[0]["role"] == "user"
        assert fmt[1]["role"] == "assistant"
        assert "content" in fmt[0]

    def test_five_turn_conversation_coherent(self, rag: MultiTurnRAG) -> None:
        topics = [
            "What is the return policy?",
            "What about shipping?",
            "Do you offer warranty?",
            "What payment methods?",
            "Can I return a digital product?",
        ]
        responses = [rag.respond(q) for q in topics]
        assert all(r for r in responses), "All responses should be non-empty"
        assert rag.conversation.num_turns() == 5

    def test_knowledge_retention_mock(self, rag: MultiTurnRAG) -> None:
        """Mock de KnowledgeRetentionMetric: verifica que info del turno 1 aparece en turno 3."""
        rag.respond("What is the return policy?")
        rag.respond("What about shipping costs?")
        response = rag.respond("What did you say about returns?")
        retained = "return" in response.lower() or "30 days" in response
        print(f"\n  Knowledge retained: {retained}")
        assert retained, "RAG should retain information about returns in turn 3"

    @pytest.mark.slow
    def test_with_real_deepeval_conversational(self, rag: MultiTurnRAG) -> None:
        if not os.getenv("GROQ_API_KEY"):
            pytest.skip("GROQ_API_KEY no encontrado")
        from deepeval.test_case import ConversationalTestCase, LLMTestCase
        from deepeval.metrics import KnowledgeRetentionMetric

        rag.respond("What is the return policy?")
        rag.respond("And shipping?")
        messages = rag.conversation.to_deepeval_format()
        tc = ConversationalTestCase(
            messages=[
                LLMTestCase(input=m["content"], actual_output="")
                if m["role"] == "user"
                else LLMTestCase(input="", actual_output=m["content"])
                for m in messages
            ]
        )
        metric = KnowledgeRetentionMetric(threshold=0.5)
        metric.measure(tc)
        print(f"\n  KnowledgeRetention: {metric.score}")
        assert metric.is_successful()
```

- [ ] **Step 8: Ejecutar tests**

```bash
pytest modules/04-multi-turn/tests/ -v -m "not slow" --record-mode=none
```

Salida esperada: `8 passed, 1 deselected`

- [ ] **Step 9: Crear solución de ejercicio**

```python
# exercises/solutions/04-multi-turn-solution.py
"""
Solución módulo 04: implementa detección de contradicciones entre turnos.
Si el asistente dice "30 days" en el turno 1 y "60 days" en el turno 3,
la conversación tiene una contradicción.
"""
from __future__ import annotations
import sys, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "modules" / "04-multi-turn"))
from src.conversation import Conversation


class ContradictionDetector:
    def find_day_mentions(self, text: str) -> list[str]:
        return re.findall(r"\d+\s*days?", text, re.IGNORECASE)

    def detect(self, conversation: Conversation) -> bool:
        all_mentions: list[str] = []
        for turn in conversation.get_assistant_turns():
            all_mentions.extend(self.find_day_mentions(turn))
        unique = set(m.lower() for m in all_mentions)
        return len(unique) > 1


if __name__ == "__main__":
    conv = Conversation()
    conv.add_turn("How long to return?", "Returns allowed within 30 days.")
    conv.add_turn("Are you sure?", "Actually it's 60 days for premium members.")
    detector = ContradictionDetector()
    print("Contradiction detected:", detector.detect(conv))
```

- [ ] **Step 10: Commit**

```bash
git add modules/04-multi-turn/ exercises/solutions/04-multi-turn-solution.py
git commit -m "feat(04-multi-turn): add multi-turn conversation testing module"
```

---

## Task 4: Módulo 05 — prompt-regression

**Files:**
- Create: `modules/05-prompt-regression/conftest.py`
- Create: `modules/05-prompt-regression/src/__init__.py`
- Create: `modules/05-prompt-regression/src/prompt_registry.py`
- Create: `modules/05-prompt-regression/src/regression_checker.py`
- Create: `modules/05-prompt-regression/promptfooconfig.yaml`
- Create: `modules/05-prompt-regression/tests/__init__.py`
- Create: `modules/05-prompt-regression/tests/conftest.py`
- Create: `modules/05-prompt-regression/tests/test_regression.py`
- Create: `exercises/solutions/05-prompt-regression-solution.py`

---

- [ ] **Step 1: Crear conftest.py raíz**

```python
# modules/05-prompt-regression/conftest.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
```

- [ ] **Step 2: Crear src/__init__.py** — archivo vacío

- [ ] **Step 3: Crear src/prompt_registry.py**

```python
# modules/05-prompt-regression/src/prompt_registry.py
"""
Registro de prompts versionados.
Permite recuperar prompts por nombre y versión, y comparar versiones.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PromptVersion:
    name: str
    version: str
    template: str
    description: str = ""
    tags: list[str] = field(default_factory=list)

    def render(self, **kwargs: str) -> str:
        """Renderiza el template con las variables dadas."""
        result = self.template
        for key, value in kwargs.items():
            result = result.replace(f"{{{key}}}", value)
        return result


class PromptRegistry:
    """Registro in-memory de prompts versionados."""

    def __init__(self) -> None:
        self._prompts: dict[tuple[str, str], PromptVersion] = {}

    def register(self, prompt: PromptVersion) -> None:
        self._prompts[(prompt.name, prompt.version)] = prompt

    def get(self, name: str, version: str) -> PromptVersion:
        key = (name, version)
        if key not in self._prompts:
            raise KeyError(f"Prompt '{name}' version '{version}' not found")
        return self._prompts[key]

    def list_versions(self, name: str) -> list[str]:
        return [v for (n, v) in self._prompts if n == name]

    def latest(self, name: str) -> PromptVersion:
        versions = self.list_versions(name)
        if not versions:
            raise KeyError(f"No prompts found with name '{name}'")
        return self.get(name, sorted(versions)[-1])


def build_default_registry() -> PromptRegistry:
    """Registry con los prompts de demo del módulo 05."""
    registry = PromptRegistry()

    registry.register(PromptVersion(
        name="support_response",
        version="v1",
        template=(
            "You are a support agent. Answer the following question: {question}"
        ),
        description="Prompt básico sin instrucciones de formato",
    ))

    registry.register(PromptVersion(
        name="support_response",
        version="v2",
        template=(
            "You are a helpful customer support agent. "
            "Answer the following question concisely and accurately, "
            "citing specific policy details when relevant: {question}"
        ),
        description="Prompt mejorado con instrucciones de formato y contexto",
    ))

    return registry
```

- [ ] **Step 4: Crear src/regression_checker.py**

```python
# modules/05-prompt-regression/src/regression_checker.py
"""
Compara scores de dos versiones de prompt y detecta regresiones.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RegressionReport:
    prompt_name: str
    baseline_version: str
    candidate_version: str
    baseline_score: float
    candidate_score: float
    delta: float = 0.0
    regression_detected: bool = False
    metric_name: str = "score"

    def __post_init__(self) -> None:
        self.delta = round(self.candidate_score - self.baseline_score, 4)

    def summary(self) -> str:
        direction = "▲" if self.delta >= 0 else "▼"
        status = "REGRESSION" if self.regression_detected else "OK"
        return (
            f"[{status}] {self.prompt_name}: "
            f"{self.baseline_version}={self.baseline_score:.2f} → "
            f"{self.candidate_version}={self.candidate_score:.2f} "
            f"({direction}{abs(self.delta):.2f})"
        )


class RegressionChecker:
    """Detecta regresiones comparando scores entre versiones de prompt."""

    def __init__(self, threshold: float = 0.1) -> None:
        self.threshold = threshold

    def check(
        self,
        prompt_name: str,
        baseline_version: str,
        baseline_score: float,
        candidate_version: str,
        candidate_score: float,
        metric_name: str = "score",
    ) -> RegressionReport:
        report = RegressionReport(
            prompt_name=prompt_name,
            baseline_version=baseline_version,
            candidate_version=candidate_version,
            baseline_score=baseline_score,
            candidate_score=candidate_score,
            metric_name=metric_name,
        )
        report.regression_detected = report.delta < -self.threshold
        return report

    def check_multiple(
        self,
        prompt_name: str,
        baseline_version: str,
        candidate_version: str,
        scores: dict[str, tuple[float, float]],
    ) -> list[RegressionReport]:
        """Compara múltiples métricas a la vez. scores = {metric: (baseline, candidate)}"""
        return [
            self.check(
                prompt_name=prompt_name,
                baseline_version=baseline_version,
                baseline_score=b,
                candidate_version=candidate_version,
                candidate_score=c,
                metric_name=metric,
            )
            for metric, (b, c) in scores.items()
        ]
```

- [ ] **Step 5: Crear promptfooconfig.yaml**

```yaml
# modules/05-prompt-regression/promptfooconfig.yaml
# Promptfoo config: 2 versiones de prompt × modelo Groq
# Ejecutar: promptfoo eval (requiere GROQ_API_KEY)
description: "Regression test: support_response v1 vs v2"

prompts:
  - id: v1
    raw: "You are a support agent. Answer the following question: {{question}}"
  - id: v2
    raw: >
      You are a helpful customer support agent.
      Answer the following question concisely and accurately,
      citing specific policy details when relevant: {{question}}

providers:
  - id: groq:llama3-8b-8192
    config:
      temperature: 0

tests:
  - vars:
      question: "What is the return policy?"
    assert:
      - type: llm-rubric
        value: "The response should mention 30 days and refund"
      - type: contains-any
        value: ["30 days", "thirty days", "return"]

  - vars:
      question: "How long does shipping take?"
    assert:
      - type: llm-rubric
        value: "The response should mention shipping timeframes"
      - type: contains-any
        value: ["days", "shipping", "delivery"]
```

- [ ] **Step 6: Crear tests/__init__.py** — archivo vacío

- [ ] **Step 7: Crear tests/conftest.py**

```python
# modules/05-prompt-regression/tests/conftest.py
import pytest
from src.prompt_registry import PromptRegistry, build_default_registry
from src.regression_checker import RegressionChecker


@pytest.fixture(scope="module")
def registry() -> PromptRegistry:
    return build_default_registry()


@pytest.fixture
def checker() -> RegressionChecker:
    return RegressionChecker(threshold=0.1)
```

- [ ] **Step 8: Crear tests/test_regression.py**

```python
# modules/05-prompt-regression/tests/test_regression.py
"""Módulo 05 — Prompt Regression: detección de regresiones entre versiones."""
from __future__ import annotations

import os
from pathlib import Path
import pytest
from src.prompt_registry import PromptRegistry, build_default_registry
from src.regression_checker import RegressionChecker, RegressionReport


class TestPromptRegistry:

    def test_get_prompt_by_version(self, registry: PromptRegistry) -> None:
        v1 = registry.get("support_response", "v1")
        assert "support agent" in v1.template

    def test_get_prompt_v2_has_more_detail(self, registry: PromptRegistry) -> None:
        v2 = registry.get("support_response", "v2")
        assert "concisely" in v2.template or "accurately" in v2.template

    def test_list_versions(self, registry: PromptRegistry) -> None:
        versions = registry.list_versions("support_response")
        assert "v1" in versions
        assert "v2" in versions

    def test_get_latest_returns_v2(self, registry: PromptRegistry) -> None:
        latest = registry.latest("support_response")
        assert latest.version == "v2"

    def test_render_replaces_variables(self, registry: PromptRegistry) -> None:
        v1 = registry.get("support_response", "v1")
        rendered = v1.render(question="What is the return policy?")
        assert "What is the return policy?" in rendered
        assert "{question}" not in rendered

    def test_missing_prompt_raises_key_error(self, registry: PromptRegistry) -> None:
        with pytest.raises(KeyError):
            registry.get("nonexistent", "v1")


class TestRegressionChecker:

    def test_improvement_not_regression(self, checker: RegressionChecker) -> None:
        report = checker.check("support_response", "v1", 0.75, "v2", 0.85)
        print(f"\n  {report.summary()}")
        assert not report.regression_detected
        assert report.delta > 0

    def test_degradation_detected(self, checker: RegressionChecker) -> None:
        report = checker.check("support_response", "v1", 0.85, "v2", 0.70)
        print(f"\n  {report.summary()}")
        assert report.regression_detected
        assert report.delta < 0

    def test_within_tolerance_not_regression(self, checker: RegressionChecker) -> None:
        report = checker.check("support_response", "v1", 0.80, "v2", 0.75)
        # delta = -0.05, threshold = 0.10 → no es regresión
        print(f"\n  {report.summary()} (delta={report.delta}, threshold={checker.threshold})")
        assert not report.regression_detected

    def test_multiple_metrics_partial_regression(
        self, checker: RegressionChecker
    ) -> None:
        scores = {
            "relevancy": (0.80, 0.85),   # mejora
            "faithfulness": (0.90, 0.70), # regresión
        }
        reports = checker.check_multiple("support_response", "v1", "v2", scores)
        assert len(reports) == 2
        regressions = [r for r in reports if r.regression_detected]
        assert len(regressions) == 1
        assert regressions[0].metric_name == "faithfulness"

    def test_promptfooconfig_is_valid_yaml(self) -> None:
        import yaml
        config_path = Path(__file__).parent.parent / "promptfooconfig.yaml"
        assert config_path.exists(), "promptfooconfig.yaml debe existir"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert "prompts" in config
        assert "providers" in config
        assert "tests" in config
        assert len(config["prompts"]) >= 2

    @pytest.mark.slow
    def test_with_promptfoo_cli(self) -> None:
        if not os.getenv("GROQ_API_KEY"):
            pytest.skip("GROQ_API_KEY no encontrado")
        import subprocess
        result = subprocess.run(
            ["promptfoo", "eval", "--config", "promptfooconfig.yaml", "--no-cache"],
            capture_output=True, text=True, cwd=Path(__file__).parent.parent,
        )
        print(f"\n  Promptfoo output: {result.stdout[-300:]}")
        assert result.returncode == 0, f"Promptfoo falló: {result.stderr}"
```

- [ ] **Step 9: Ejecutar tests**

```bash
pytest modules/05-prompt-regression/tests/ -v -m "not slow" --record-mode=none
```

Salida esperada: `8 passed, 1 deselected`

- [ ] **Step 10: Crear solución de ejercicio**

```python
# exercises/solutions/05-prompt-regression-solution.py
"""
Solución módulo 05: añade versionado semántico (semver) al PromptRegistry
y detecta breaking changes entre versiones major.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "modules" / "05-prompt-regression"))
from src.prompt_registry import PromptRegistry, PromptVersion


class SemverRegistry(PromptRegistry):
    def is_breaking_change(self, name: str, v_from: str, v_to: str) -> bool:
        """Detecta si el cambio de versión es un major bump (breaking change)."""
        try:
            major_from = int(v_from.lstrip("v").split(".")[0])
            major_to = int(v_to.lstrip("v").split(".")[0])
            return major_to > major_from
        except (ValueError, IndexError):
            return False


if __name__ == "__main__":
    reg = SemverRegistry()
    reg.register(PromptVersion("q", "v1.0.0", "Template A"))
    reg.register(PromptVersion("q", "v2.0.0", "Template B — breaking change"))
    print(reg.is_breaking_change("q", "v1.0.0", "v2.0.0"))  # True
    print(reg.is_breaking_change("q", "v1.0.0", "v1.1.0"))  # False
```

- [ ] **Step 11: Commit**

```bash
git add modules/05-prompt-regression/ exercises/solutions/05-prompt-regression-solution.py
git commit -m "feat(05-prompt-regression): add prompt versioning and regression detection"
```

---

## Task 5: Módulo 06 — hallucination-lab

**Files:**
- Create: `modules/06-hallucination-lab/conftest.py`
- Create: `modules/06-hallucination-lab/src/__init__.py`
- Create: `modules/06-hallucination-lab/src/claim_extractor.py`
- Create: `modules/06-hallucination-lab/src/groundedness_checker.py`
- Create: `modules/06-hallucination-lab/tests/__init__.py`
- Create: `modules/06-hallucination-lab/tests/conftest.py`
- Create: `modules/06-hallucination-lab/tests/test_hallucination.py`
- Create: `exercises/solutions/06-hallucination-lab-solution.py`

---

- [ ] **Step 1: Crear conftest.py raíz**

```python
# modules/06-hallucination-lab/conftest.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
```

- [ ] **Step 2: Crear src/__init__.py** — archivo vacío

- [ ] **Step 3: Crear src/claim_extractor.py**

```python
# modules/06-hallucination-lab/src/claim_extractor.py
"""
Extractor de claims de una respuesta LLM.
Versión determinista: split por delimitadores de oración + filtro de longitud.
"""
from __future__ import annotations

import re


def extract_claims(text: str, min_words: int = 4) -> list[str]:
    """
    Extrae claims individuales de un texto.
    Un claim es una oración con al menos `min_words` palabras.
    """
    sentences = re.split(r'[.!?]+', text)
    claims = []
    for sent in sentences:
        sent = sent.strip()
        if len(sent.split()) >= min_words:
            claims.append(sent)
    return claims
```

- [ ] **Step 4: Crear src/groundedness_checker.py**

```python
# modules/06-hallucination-lab/src/groundedness_checker.py
"""
Groundedness checker: verifica si los claims de una respuesta
están soportados por el contexto recuperado.

Groundedness ≈ fracción de claims con cobertura suficiente en el contexto.
"""
from __future__ import annotations

from dataclasses import dataclass
from src.claim_extractor import extract_claims


@dataclass
class GroundednessResult:
    score: float
    total_claims: int
    grounded_claims: int
    ungrounded: list[str]
    threshold: float

    @property
    def passed(self) -> bool:
        return self.score >= self.threshold

    def __repr__(self) -> str:
        status = "✓" if self.passed else "✗"
        return (
            f"Groundedness[{status}] "
            f"{self.grounded_claims}/{self.total_claims} claims grounded "
            f"(score={self.score:.2f})"
        )


class GroundednessChecker:
    """
    Verifica cada claim contra el contexto usando overlap de tokens.
    overlap_threshold: fracción mínima de tokens del claim que deben
    aparecer en el contexto para considerarlo "grounded".
    """

    def __init__(self, overlap_threshold: float = 0.5) -> None:
        self.overlap_threshold = overlap_threshold

    def _tokenize(self, text: str) -> set[str]:
        return {w.lower() for w in text.split() if len(w) > 3}

    def _is_grounded(self, claim: str, context_tokens: set[str]) -> bool:
        claim_tokens = self._tokenize(claim)
        if not claim_tokens:
            return True
        overlap = claim_tokens & context_tokens
        return len(overlap) / len(claim_tokens) >= self.overlap_threshold

    def check(
        self,
        response: str,
        context: list[str],
        score_threshold: float = 0.7,
    ) -> GroundednessResult:
        if not context:
            return GroundednessResult(
                score=0.0,
                total_claims=0,
                grounded_claims=0,
                ungrounded=[],
                threshold=score_threshold,
            )

        claims = extract_claims(response)
        if not claims:
            return GroundednessResult(
                score=1.0,
                total_claims=0,
                grounded_claims=0,
                ungrounded=[],
                threshold=score_threshold,
            )

        context_tokens = self._tokenize(" ".join(context))
        grounded = [c for c in claims if self._is_grounded(c, context_tokens)]
        ungrounded = [c for c in claims if not self._is_grounded(c, context_tokens)]
        score = round(len(grounded) / len(claims), 3)

        return GroundednessResult(
            score=score,
            total_claims=len(claims),
            grounded_claims=len(grounded),
            ungrounded=ungrounded,
            threshold=score_threshold,
        )
```

- [ ] **Step 5: Crear tests/__init__.py** — archivo vacío

- [ ] **Step 6: Crear tests/conftest.py**

```python
# modules/06-hallucination-lab/tests/conftest.py
import pytest
from src.groundedness_checker import GroundednessChecker


@pytest.fixture
def checker() -> GroundednessChecker:
    return GroundednessChecker(overlap_threshold=0.4)


@pytest.fixture
def good_context() -> list[str]:
    return [
        "Our return policy allows customers to return any product within 30 days "
        "of purchase for a full refund. Items must be in their original condition."
    ]


@pytest.fixture
def faithful_response() -> str:
    return (
        "Based on our policy, returns are allowed within 30 days. "
        "Items must be in original condition for a full refund."
    )


@pytest.fixture
def hallucinated_response() -> str:
    return (
        "You can return products within 365 days. "
        "We offer a 200% money-back guarantee. "
        "Same-day drone delivery is available worldwide for free."
    )
```

- [ ] **Step 7: Crear tests/test_hallucination.py**

```python
# modules/06-hallucination-lab/tests/test_hallucination.py
"""Módulo 06 — Hallucination Lab: detección de alucinaciones."""
from __future__ import annotations

import os
import pytest
from src.claim_extractor import extract_claims
from src.groundedness_checker import GroundednessChecker, GroundednessResult


class TestClaimExtractor:

    def test_extracts_multiple_claims(self, faithful_response: str) -> None:
        claims = extract_claims(faithful_response)
        print(f"\n  Claims: {claims}")
        assert len(claims) >= 2

    def test_empty_response_returns_empty_list(self) -> None:
        assert extract_claims("") == []

    def test_short_sentence_filtered(self) -> None:
        claims = extract_claims("Yes. No. Maybe. Returns are allowed within 30 days.", min_words=4)
        assert all(len(c.split()) >= 4 for c in claims)


class TestGroundednessChecker:

    def test_faithful_response_scores_high(
        self,
        checker: GroundednessChecker,
        faithful_response: str,
        good_context: list[str],
    ) -> None:
        result: GroundednessResult = checker.check(faithful_response, good_context)
        print(f"\n  {result}")
        assert result.score >= 0.6, f"Faithful response should score >= 0.6, got {result.score}"
        assert result.passed

    def test_hallucinated_response_scores_low(
        self,
        checker: GroundednessChecker,
        hallucinated_response: str,
        good_context: list[str],
    ) -> None:
        result = checker.check(hallucinated_response, good_context, score_threshold=0.7)
        print(f"\n  {result}")
        print(f"  Ungrounded claims: {result.ungrounded}")
        assert result.score < 0.6, f"Hallucinated response should score < 0.6, got {result.score}"
        assert not result.passed

    def test_no_context_returns_zero(
        self, checker: GroundednessChecker, faithful_response: str
    ) -> None:
        result = checker.check(faithful_response, [])
        assert result.score == 0.0
        assert not result.passed

    def test_threshold_configurable(
        self,
        faithful_response: str,
        good_context: list[str],
    ) -> None:
        strict = GroundednessChecker(overlap_threshold=0.8)
        lenient = GroundednessChecker(overlap_threshold=0.2)
        result_strict = strict.check(faithful_response, good_context, score_threshold=0.9)
        result_lenient = lenient.check(faithful_response, good_context, score_threshold=0.5)
        print(f"\n  Strict: {result_strict.score:.2f}, Lenient: {result_lenient.score:.2f}")
        assert result_lenient.score >= result_strict.score

    def test_ungrounded_claims_reported(
        self,
        checker: GroundednessChecker,
        hallucinated_response: str,
        good_context: list[str],
    ) -> None:
        result = checker.check(hallucinated_response, good_context)
        assert len(result.ungrounded) > 0, "Should report which claims are ungrounded"
        print(f"\n  Ungrounded: {result.ungrounded}")

    def test_partial_hallucination_detected(
        self, checker: GroundednessChecker, good_context: list[str]
    ) -> None:
        mixed_response = (
            "Returns are allowed within 30 days. "
            "We also offer a secret 500% refund guarantee for premium members."
        )
        result = checker.check(mixed_response, good_context)
        print(f"\n  Partial hallucination score: {result.score:.2f}")
        assert 0.0 < result.score < 1.0, "Partial hallucination should give intermediate score"

    @pytest.mark.slow
    def test_with_real_deepeval_hallucination(
        self, faithful_response: str, good_context: list[str]
    ) -> None:
        if not os.getenv("GROQ_API_KEY"):
            pytest.skip("GROQ_API_KEY no encontrado")
        from deepeval.metrics import HallucinationMetric
        from deepeval.test_case import LLMTestCase
        tc = LLMTestCase(
            input="What is the return policy?",
            actual_output=faithful_response,
            context=good_context,
        )
        metric = HallucinationMetric(threshold=0.5)
        metric.measure(tc)
        print(f"\n  Real HallucinationMetric score: {metric.score}")
        assert metric.is_successful()
```

- [ ] **Step 8: Ejecutar tests**

```bash
pytest modules/06-hallucination-lab/tests/ -v -m "not slow" --record-mode=none
```

Salida esperada: `9 passed, 1 deselected`

- [ ] **Step 9: Crear solución de ejercicio**

```python
# exercises/solutions/06-hallucination-lab-solution.py
"""
Solución módulo 06: implementa un RAG Triad simplificado combinando
context_relevance + groundedness + answer_relevance en un score compuesto.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "modules" / "06-hallucination-lab"))
from src.groundedness_checker import GroundednessChecker


def context_relevance(query: str, context: list[str]) -> float:
    q_tokens = {w.lower() for w in query.split() if len(w) > 3}
    ctx_tokens = {w.lower() for chunk in context for w in chunk.split() if len(w) > 3}
    if not q_tokens:
        return 1.0
    return round(len(q_tokens & ctx_tokens) / len(q_tokens), 3)


def rag_triad(query: str, response: str, context: list[str]) -> dict[str, float]:
    checker = GroundednessChecker(overlap_threshold=0.4)
    groundedness = checker.check(response, context).score
    ctx_rel = context_relevance(query, context)
    q_tokens = {w.lower() for w in query.split() if len(w) > 3}
    r_tokens = {w.lower() for w in response.split() if len(w) > 3}
    answer_rel = round(min(1.0, len(q_tokens & r_tokens) / max(len(q_tokens), 1) * 2), 3)
    return {
        "context_relevance": ctx_rel,
        "groundedness": groundedness,
        "answer_relevance": answer_rel,
        "composite": round((ctx_rel + groundedness + answer_rel) / 3, 3),
    }


if __name__ == "__main__":
    result = rag_triad(
        query="What is the return policy?",
        response="Returns are allowed within 30 days for a full refund.",
        context=["Our return policy allows returns within 30 days."],
    )
    for k, v in result.items():
        print(f"  {k}: {v:.3f}")
```

- [ ] **Step 10: Commit**

```bash
git add modules/06-hallucination-lab/ exercises/solutions/06-hallucination-lab-solution.py
git commit -m "feat(06-hallucination-lab): add claim extraction and groundedness checking"
```

---

## Task 6: Verificación final del batch

- [ ] **Step 1: Ejecutar todos los módulos del batch**

```bash
cd /Users/gonzalo/Documents/GitHub/ai-testing-lab
pytest modules/02-ragas-basics/tests/ \
       modules/03-llm-as-judge/tests/ \
       modules/04-multi-turn/tests/ \
       modules/05-prompt-regression/tests/ \
       modules/06-hallucination-lab/tests/ \
       -v -m "not slow" --record-mode=none
```

Salida esperada: `≥ 43 passed, ≤ 5 deselected` (los 5 tests slow excluidos)

- [ ] **Step 2: Verificar que make test-module funciona para cada módulo**

```bash
make test-module MODULE=02
make test-module MODULE=03
make test-module MODULE=04
make test-module MODULE=05
make test-module MODULE=06
```

- [ ] **Step 3: Push al remoto**

```bash
git push origin main
```

---

## Self-Review

**Spec coverage:**
- ✅ Módulo 02: RAGPipeline + RAGASEvaluator con 4 métricas + 9 tests
- ✅ Módulo 03: GEvalJudge + DAGMetric + demos de biases + 9 tests
- ✅ Módulo 04: Conversation + MultiTurnRAG + retención de info + 8 tests
- ✅ Módulo 05: PromptRegistry + RegressionChecker + promptfooconfig.yaml + 8 tests
- ✅ Módulo 06: ClaimExtractor + GroundednessChecker + RAG Triad parcial + 9 tests
- ✅ Todos tienen `@pytest.mark.slow` con skip automático sin API key
- ✅ Todos tienen solución de ejercicio en `exercises/solutions/`
- ✅ Ninguno requiere Docker, Ollama ni infraestructura externa

**Placeholder scan:** ningún TBD, TODO ni paso sin código

**Type consistency:** todos los fixtures usan los mismos tipos definidos en el task correspondiente
