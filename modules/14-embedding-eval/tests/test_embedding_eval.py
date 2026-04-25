from __future__ import annotations

import numpy as np
import pytest
from embedding_evaluator import (
    EmbeddingRegressionChecker,
    MockEmbeddingModel,
    SemanticSimilarityMetric,
    SimilarityResult,
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
