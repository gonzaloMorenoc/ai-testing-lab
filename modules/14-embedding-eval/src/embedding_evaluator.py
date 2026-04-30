from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Protocol

import numpy as np


class EmbeddingModel(Protocol):
    def encode(self, texts: list[str]) -> np.ndarray: ...


class MockEmbeddingModel:
    """Deterministic bag-of-words embedding model for testing (no API calls)."""

    def __init__(self, dim: int = 64) -> None:
        self._dim = dim

    def _embed_one(self, text: str) -> np.ndarray:
        words = text.lower().split()
        vec = np.zeros(self._dim, dtype=np.float64)
        for word in words:
            digest = hashlib.md5(word.encode(), usedforsecurity=False).digest()
            seed = int.from_bytes(digest[:4], "little")
            rng = np.random.default_rng(seed)
            vec += rng.standard_normal(self._dim)
        norm = np.linalg.norm(vec)
        if norm > 1e-10:
            vec /= norm
        return vec

    def encode(self, texts: list[str]) -> np.ndarray:
        return np.array([self._embed_one(t) for t in texts])


@dataclass
class SimilarityResult:
    expected: str
    actual: str
    similarity: float
    passed: bool
    threshold: float


@dataclass
class EmbeddingRegressionReport:
    results: list[SimilarityResult] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed(self) -> int:
        return len(self.results) - self.passed

    @property
    def pass_rate(self) -> float:
        if not self.results:
            return 0.0
        return round(self.passed / len(self.results), 4)

    def summary(self) -> str:
        return (
            f"EmbeddingRegressionReport: {len(self.results)} checks, "
            f"pass_rate={self.pass_rate:.1%}, "
            f"passed={self.passed}, failed={self.failed}"
        )


class SemanticSimilarityMetric:
    """Cosine similarity between expected and actual outputs."""

    def __init__(self, model: EmbeddingModel, threshold: float = 0.7) -> None:
        self._model = model
        self.threshold = threshold

    def _cosine(self, a: np.ndarray, b: np.ndarray) -> float:
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a < 1e-10 or norm_b < 1e-10:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    def measure(self, expected: str, actual: str) -> SimilarityResult:
        vecs = self._model.encode([expected, actual])
        sim = self._cosine(vecs[0], vecs[1])
        return SimilarityResult(
            expected=expected,
            actual=actual,
            similarity=round(sim, 4),
            passed=sim >= self.threshold,
            threshold=self.threshold,
        )

    def measure_batch(self, pairs: list[tuple[str, str]]) -> list[SimilarityResult]:
        return [self.measure(exp, act) for exp, act in pairs]


class EmbeddingRegressionChecker:
    """Compare baseline vs candidate outputs against expected using cosine similarity."""

    def __init__(self, model: EmbeddingModel, threshold: float = 0.7) -> None:
        self._metric = SemanticSimilarityMetric(model, threshold)

    def check(
        self,
        expected_outputs: list[str],
        candidate_outputs: list[str],
    ) -> EmbeddingRegressionReport:
        if len(expected_outputs) != len(candidate_outputs):
            raise ValueError(
                f"expected_outputs and candidate_outputs must have equal length, "
                f"got {len(expected_outputs)} vs {len(candidate_outputs)}"
            )
        results = [
            self._metric.measure(exp, cand)
            for exp, cand in zip(expected_outputs, candidate_outputs, strict=True)
        ]
        return EmbeddingRegressionReport(results=results)
