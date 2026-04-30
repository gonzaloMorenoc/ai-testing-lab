from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from embedding_evaluator import EmbeddingModel


@dataclass
class DriftResult:
    centroid_shift: float
    threshold: float
    triggered: bool
    message: str


def compute_centroid_shift(
    reference: list[str],
    current: list[str],
    model: EmbeddingModel,
) -> float:
    """Cosine distance between the centroid of reference and current embeddings."""
    ref_vecs = model.encode(reference)
    cur_vecs = model.encode(current)
    ref_centroid = ref_vecs.mean(axis=0)
    cur_centroid = cur_vecs.mean(axis=0)
    norm_r = np.linalg.norm(ref_centroid)
    norm_c = np.linalg.norm(cur_centroid)
    if norm_r < 1e-10 or norm_c < 1e-10:
        return 1.0
    cosine_sim = float(np.dot(ref_centroid, cur_centroid) / (norm_r * norm_c))
    return round(1.0 - cosine_sim, 6)


def semantic_drift_alert(
    model: EmbeddingModel,
    threshold: float = 0.1,
) -> Callable[[list[str], list[str]], DriftResult]:
    def check(reference: list[str], current: list[str]) -> DriftResult:
        shift = compute_centroid_shift(reference, current, model)
        triggered = shift > threshold
        return DriftResult(
            centroid_shift=shift,
            threshold=threshold,
            triggered=triggered,
            message=f"centroid_shift={shift:.4f} {'>' if triggered else '<='} {threshold}",
        )

    return check
