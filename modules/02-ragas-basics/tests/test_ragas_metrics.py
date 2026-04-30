from __future__ import annotations

import os

import pytest

from src.rag_pipeline import RAGPipeline
from src.ragas_evaluator import RAGASEvaluator, RAGASScores


class TestFaithfulness:
    def test_faithful_response_scores_high(
        self, evaluator: RAGASEvaluator, returns_result: dict
    ) -> None:
        score = evaluator.faithfulness(returns_result["response"], returns_result["context"])
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
        score = evaluator.answer_relevancy(returns_result["query"], returns_result["response"])
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

    def test_batch_evaluation(self, pipeline: RAGPipeline, evaluator: RAGASEvaluator) -> None:
        queries = [
            "What is the return policy?",
            "How long does shipping take?",
            "Is there a warranty?",
        ]
        results = [pipeline.run(q) for q in queries]
        scores = [evaluator.evaluate(r["query"], r["response"], r["context"]) for r in results]
        avg_faithfulness = sum(s.faithfulness for s in scores) / len(scores)
        print(f"\n  Avg faithfulness over batch: {avg_faithfulness:.2f}")
        assert avg_faithfulness >= 0.6

    @pytest.mark.slow
    def test_with_real_ragas(self, pipeline: RAGPipeline) -> None:
        if not os.getenv("GROQ_API_KEY"):
            pytest.skip("GROQ_API_KEY no encontrado")
        try:
            from datasets import Dataset
            from ragas import evaluate
            from ragas.metrics import answer_relevancy, faithfulness
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
