from __future__ import annotations

import numpy as np
import pytest


@pytest.fixture
def reference_scores() -> list[float]:
    rng = np.random.default_rng(42)
    return rng.normal(loc=0.8, scale=0.05, size=200).tolist()


@pytest.fixture
def identical_scores(reference_scores: list[float]) -> list[float]:
    return list(reference_scores)


@pytest.fixture
def shifted_scores() -> list[float]:
    rng = np.random.default_rng(99)
    return rng.normal(loc=0.3, scale=0.1, size=200).tolist()


@pytest.fixture
def dropped_scores(reference_scores: list[float]) -> list[float]:
    return [s * 0.75 for s in reference_scores]  # 25% drop
