"""Tests del evaluator y del gate ΔNDCG@5 ≥ +0.05."""

import pytest

from retrieval_evaluator import (
    JUSTIFICATION_THRESHOLD_NDCG,
    ComparisonReport,
    evaluate_technique,
    map_at_k,
    mrr_at_k,
    ndcg_at_k,
)
from retrieval_techniques import BaselineDenseRetriever, HyDERetriever


class TestMetrics:
    def test_ndcg_perfect_ranking(self):
        qrels = {"a": 3.0, "b": 2.0, "c": 1.0}
        retrieved = ["a", "b", "c"]
        assert ndcg_at_k(retrieved, qrels, k=3) == pytest.approx(1.0)

    def test_ndcg_no_relevant_returns_zero(self):
        qrels = {"a": 1.0}
        retrieved = ["x", "y", "z"]
        assert ndcg_at_k(retrieved, qrels, k=3) == 0.0

    def test_mrr_first_relevant_at_position_1(self):
        qrels = {"a": 1.0}
        retrieved = ["a", "b"]
        assert mrr_at_k(retrieved, qrels) == 1.0

    def test_mrr_first_relevant_at_position_3(self):
        qrels = {"c": 1.0}
        retrieved = ["a", "b", "c"]
        assert mrr_at_k(retrieved, qrels) == pytest.approx(1 / 3)

    def test_mrr_no_relevant_returns_zero(self):
        assert mrr_at_k(["x"], {"a": 1.0}) == 0.0

    def test_map_with_relevant_documents(self):
        qrels = {"a": 1.0, "c": 1.0}
        retrieved = ["a", "b", "c"]
        # P@1=1.0, P@3=2/3; AP = (1.0 + 2/3) / 2 = 0.833
        assert map_at_k(retrieved, qrels, k=3) > 0.5


class TestComparisonReport:
    def test_justified_when_delta_ndcg_above_threshold(self):
        report = ComparisonReport.from_scores(
            baseline_scores={"ndcg5": 0.50, "mrr5": 0.5, "map5": 0.5},
            advanced_scores={"ndcg5": 0.60, "mrr5": 0.5, "map5": 0.5},
            baseline_overhead={"latency_ms": 0, "llm_calls": 0},
            advanced_overhead={"latency_ms": 350, "llm_calls": 1},
        )
        assert report.justified
        assert report.delta_ndcg == pytest.approx(0.10)

    def test_not_justified_when_delta_too_small(self):
        report = ComparisonReport.from_scores(
            baseline_scores={"ndcg5": 0.50, "mrr5": 0.5, "map5": 0.5},
            advanced_scores={"ndcg5": 0.52, "mrr5": 0.5, "map5": 0.5},
            baseline_overhead={"latency_ms": 0, "llm_calls": 0},
            advanced_overhead={"latency_ms": 350, "llm_calls": 1},
        )
        assert not report.justified

    def test_threshold_is_0_05(self):
        assert JUSTIFICATION_THRESHOLD_NDCG == 0.05

    def test_latency_overhead(self):
        report = ComparisonReport.from_scores(
            baseline_scores={"ndcg5": 0.5, "mrr5": 0.5, "map5": 0.5},
            advanced_scores={"ndcg5": 0.6, "mrr5": 0.5, "map5": 0.5},
            baseline_overhead={"latency_ms": 100, "llm_calls": 0},
            advanced_overhead={"latency_ms": 450, "llm_calls": 1},
        )
        assert report.latency_overhead_ms == 350
        assert report.llm_calls_overhead == 1


class TestEvaluateTechnique:
    def test_compares_baseline_vs_hyde(self, sample_docs, qrels_by_query):
        baseline = BaselineDenseRetriever(sample_docs)
        hyde = HyDERetriever(
            sample_docs,
            mock_llm=lambda q: {
                "comida valenciana": "paella arroz azafran bomba",
                "gato come": "felino pescado fresco mañana",
                "lenguaje programacion": "python data science software",
            }.get(q, q),
        )
        report = evaluate_technique(baseline, hyde, qrels_by_query, top_k=5)
        assert isinstance(report, ComparisonReport)
        # latency_overhead debe ser positivo (HyDE añade 350 ms)
        assert report.latency_overhead_ms == 350.0
