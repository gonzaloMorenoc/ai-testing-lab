from __future__ import annotations

import numpy as np

_N_BINS = 10
_EPSILON = 1e-10


def _proportions(data: np.ndarray, bins: np.ndarray) -> np.ndarray:
    counts, _ = np.histogram(data, bins=bins)
    # Laplace smoothing: add 0.5 to each bin to prevent log(0) blow-up
    smoothed = counts + 0.5
    return smoothed / smoothed.sum()


def compute_psi(
    reference: list[float] | np.ndarray,
    current: list[float] | np.ndarray,
    n_bins: int = _N_BINS,
) -> float:
    """Population Stability Index between reference and current distributions."""
    ref = np.asarray(reference, dtype=float)
    cur = np.asarray(current, dtype=float)

    combined = np.concatenate([ref, cur])
    bins = np.linspace(combined.min(), combined.max() + _EPSILON, n_bins + 1)

    ref_props = _proportions(ref, bins)
    cur_props = _proportions(cur, bins)

    psi = float(np.sum((cur_props - ref_props) * np.log(cur_props / ref_props)))
    return round(psi, 4)
