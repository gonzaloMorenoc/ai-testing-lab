from __future__ import annotations

import sys
from pathlib import Path

import pytest

_SRC = str(Path(__file__).parent.parent / "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from embedding_evaluator import (  # noqa: E402
    EmbeddingRegressionChecker,
    MockEmbeddingModel,
    SemanticSimilarityMetric,
)


@pytest.fixture(scope="session")
def model() -> MockEmbeddingModel:
    return MockEmbeddingModel(dim=64)


@pytest.fixture(scope="session")
def metric(model: MockEmbeddingModel) -> SemanticSimilarityMetric:
    return SemanticSimilarityMetric(model, threshold=0.5)


@pytest.fixture(scope="session")
def checker(model: MockEmbeddingModel) -> EmbeddingRegressionChecker:
    return EmbeddingRegressionChecker(model, threshold=0.5)
