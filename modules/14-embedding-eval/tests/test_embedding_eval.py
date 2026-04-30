from __future__ import annotations

import numpy as np
import pytest
from embedding_evaluator import (
    EmbeddingRegressionChecker,
    MockEmbeddingModel,
    SemanticSimilarityMetric,
    SimilarityResult,
)
from retrieval_metrics import (
    RETRIEVAL_THRESHOLD,
    RetrievalMetricsReport,
    evaluate_retrieval,
    map_at_k,
    mrr_at_k,
    ndcg_at_k,
)
from semantic_drift import DriftResult, compute_centroid_shift, semantic_drift_alert


class TestMockEmbeddingModel:

    def test_encode_returns_correct_shape(self, model: MockEmbeddingModel) -> None:
        texts = ["hello world", "foo bar", "baz"]
        vecs = model.encode(texts)
        assert vecs.shape == (3, 64)

    def test_encode_is_deterministic(self, model: MockEmbeddingModel) -> None:
        text = "the quick brown fox"
        v1 = model.encode([text])
        v2 = model.encode([text])
        np.testing.assert_array_equal(v1, v2)

    def test_encode_different_texts_differ(self, model: MockEmbeddingModel) -> None:
        vecs = model.encode(["machine learning", "deep neural network"])
        assert not np.allclose(vecs[0], vecs[1])

    def test_encode_unit_normalized(self, model: MockEmbeddingModel) -> None:
        vecs = model.encode(["normalization test text here"])
        norm = float(np.linalg.norm(vecs[0]))
        assert abs(norm - 1.0) < 1e-6


class TestSemanticSimilarityMetric:

    def test_identical_texts_high_similarity(self, metric: SemanticSimilarityMetric) -> None:
        result = metric.measure("The capital of France is Paris.", "The capital of France is Paris.")
        print(f"\n  identical similarity: {result.similarity}")
        assert result.similarity > 0.99

    def test_similar_texts_pass_threshold(self, metric: SemanticSimilarityMetric) -> None:
        result = metric.measure(
            "The sky is blue.", "The color of the sky is blue."
        )
        print(f"\n  similar similarity: {result.similarity}")
        assert isinstance(result, SimilarityResult)
        assert result.similarity >= 0.0

    def test_result_has_required_fields(self, metric: SemanticSimilarityMetric) -> None:
        result = metric.measure("hello", "world")
        assert result.expected == "hello"
        assert result.actual == "world"
        assert isinstance(result.similarity, float)
        assert isinstance(result.passed, bool)
        assert result.threshold == metric.threshold

    def test_batch_returns_correct_count(self, metric: SemanticSimilarityMetric) -> None:
        pairs = [("a", "b"), ("c", "d"), ("e", "f")]
        results = metric.measure_batch(pairs)
        assert len(results) == 3
        assert all(isinstance(r, SimilarityResult) for r in results)


class TestEmbeddingRegressionChecker:

    def test_identical_outputs_all_pass(self, checker: EmbeddingRegressionChecker) -> None:
        expected = ["The answer is 42.", "Paris is in France."]
        candidate = ["The answer is 42.", "Paris is in France."]
        report = checker.check(expected, candidate)
        print(f"\n  {report.summary()}")
        assert report.pass_rate == 1.0
        assert report.failed == 0

    def test_mismatched_length_raises(self, checker: EmbeddingRegressionChecker) -> None:
        with pytest.raises(ValueError, match="equal length"):
            checker.check(["a", "b"], ["x"])

    def test_report_summary_contains_required_info(self, checker: EmbeddingRegressionChecker) -> None:
        report = checker.check(["hello world"], ["hello world"])
        summary = report.summary()
        assert "pass_rate=" in summary
        assert "passed=" in summary
        assert "failed=" in summary


class TestSemanticDrift:

    def test_identical_corpus_near_zero_shift(self, model: MockEmbeddingModel) -> None:
        ref = ["cat sat on mat", "dog ran in park", "bird flew over river"]
        shift = compute_centroid_shift(ref, ref, model)
        print(f"\n  identical corpus shift: {shift}")
        assert shift < 0.01

    def test_shifted_corpus_higher_shift(self, model: MockEmbeddingModel) -> None:
        ref = ["machine learning model training", "neural network weights"]
        cur = ["pizza margherita olive oil", "guitar chords melody"]
        shift = compute_centroid_shift(ref, cur, model)
        print(f"\n  shifted corpus shift: {shift}")
        assert shift > 0.0

    def test_drift_alert_triggered_on_shift(self, model: MockEmbeddingModel) -> None:
        ref = ["apple banana cherry", "date elderberry fig"]
        cur = ["quantum physics string theory", "black hole event horizon"]
        alert = semantic_drift_alert(model, threshold=0.01)
        result = alert(ref, cur)
        print(f"\n  {result.message}")
        assert isinstance(result, DriftResult)
        assert result.centroid_shift >= 0.0

    def test_drift_alert_not_triggered_same_corpus(self, model: MockEmbeddingModel) -> None:
        ref = ["the quick brown fox", "jumps over lazy dog"]
        alert = semantic_drift_alert(model, threshold=0.5)
        result = alert(ref, ref)
        assert result.triggered is False
        assert result.centroid_shift < 0.01


class TestRetrievalMetrics:

    # --- ndcg_at_k ---

    def test_ndcg_perfect_ranking(self) -> None:
        result = ndcg_at_k({0, 1, 2}, [0, 1, 2, 3, 4], k=3)
        assert abs(result - 1.0) < 1e-9

    def test_ndcg_no_relevant_retrieved(self) -> None:
        result = ndcg_at_k({5, 6}, [0, 1, 2], k=3)
        assert result == 0.0

    def test_ndcg_partial_ranking(self) -> None:
        # relevant={0,2}, ranked=[2,1,0]: relevant docs at positions 1 and 3
        result = ndcg_at_k({0, 2}, [2, 1, 0], k=3)
        assert 0.0 < result < 1.0

    def test_ndcg_k_larger_than_list(self) -> None:
        # k=10 but list has only 3 items — must not raise
        result = ndcg_at_k({0, 1}, [0, 1, 2], k=10)
        assert result == 1.0

    def test_ndcg_empty_relevant(self) -> None:
        result = ndcg_at_k(set(), [0, 1, 2], k=3)
        assert result == 0.0

    # --- mrr_at_k ---

    def test_mrr_first_position(self) -> None:
        result = mrr_at_k({0}, [0, 1, 2], k=3)
        assert abs(result - 1.0) < 1e-9

    def test_mrr_second_position(self) -> None:
        result = mrr_at_k({1}, [0, 1, 2], k=3)
        assert abs(result - 0.5) < 1e-9

    def test_mrr_not_in_top_k(self) -> None:
        result = mrr_at_k({5}, [0, 1, 2], k=3)
        assert result == 0.0

    def test_mrr_multiple_relevant(self) -> None:
        # relevant at positions 1 and 2; MRR = 1/1 = 1.0 (first hit at pos 1)
        result = mrr_at_k({0, 1}, [0, 1, 2], k=3)
        assert abs(result - 1.0) < 1e-9

    # --- map_at_k ---

    def test_map_perfect(self) -> None:
        # relevant={0,1,2}, ranked=[0,1,2], k=3
        # |R|=3, hits at 1,2,3 → AP = (1/3)*(1 + 2/2 + 3/3) = (1/3)*3 = 1.0
        result = map_at_k({0, 1, 2}, [0, 1, 2], k=3)
        assert abs(result - 1.0) < 1e-9

    def test_map_none_relevant(self) -> None:
        result = map_at_k({5, 6}, [0, 1, 2], k=3)
        assert result == 0.0

    def test_map_interleaved(self) -> None:
        # relevant={0,2}, ranked=[0,1,2], k=3
        # |R| = min(2, 3) = 2
        # pos 1: 0 relevant → hits=1, P@1=1/1=1.0
        # pos 2: 1 not relevant
        # pos 3: 2 relevant → hits=2, P@3=2/3
        # AP = (1/2)*(1.0 + 2/3) = (1/2)*(5/3) = 5/6
        expected = 5.0 / 6.0
        result = map_at_k({0, 2}, [0, 1, 2], k=3)
        assert abs(result - expected) < 1e-9

    # --- evaluate_retrieval ---

    def test_evaluate_retrieval_perfect(self) -> None:
        relevant_sets = [{0, 1, 2}, {3, 4}]
        ranked_lists = [[0, 1, 2, 5], [3, 4, 6]]
        report = evaluate_retrieval(relevant_sets, ranked_lists, k=3, threshold=0.5)
        assert report.passed is True
        assert report.ndcg == 1.0
        assert report.mrr == 1.0
        assert report.map_score == 1.0

    def test_evaluate_retrieval_mismatched_lengths(self) -> None:
        with pytest.raises(ValueError, match="igual longitud"):
            evaluate_retrieval([{0}], [[0], [1]], k=3)

    def test_evaluate_retrieval_empty(self) -> None:
        with pytest.raises(ValueError, match="al menos una query"):
            evaluate_retrieval([], [], k=3)

    def test_evaluate_retrieval_report_fields(self) -> None:
        relevant_sets = [{0}, {1}]
        ranked_lists = [[0, 2, 3], [1, 2, 3]]
        report = evaluate_retrieval(relevant_sets, ranked_lists, k=5, threshold=0.5)
        assert isinstance(report, RetrievalMetricsReport)
        assert report.k == 5
        assert report.num_queries == 2
        assert 0.0 <= report.ndcg <= 1.0
        assert 0.0 <= report.mrr <= 1.0
        assert 0.0 <= report.map_score <= 1.0
        assert isinstance(report.passed, bool)

    def test_retrieval_threshold_constant(self) -> None:
        assert RETRIEVAL_THRESHOLD == 0.5

    def test_evaluate_retrieval_below_threshold_not_passed(self) -> None:
        # No relevant docs retrieved → all metrics = 0.0 → passed=False
        relevant_sets = [{99}]
        ranked_lists = [[0, 1, 2]]
        report = evaluate_retrieval(relevant_sets, ranked_lists, k=3, threshold=0.5)
        assert report.passed is False
        assert report.ndcg == 0.0
        assert report.mrr == 0.0
        assert report.map_score == 0.0
