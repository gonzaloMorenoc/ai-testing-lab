from __future__ import annotations

import math
from dataclasses import dataclass

# z-scores for common significance levels (two-tailed)
_Z_CRITICAL: dict[float, float] = {0.10: 1.645, 0.05: 1.960, 0.01: 2.576}


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


def is_significant(
    delta: float,
    n_samples: int,
    baseline_score: float,
    alpha: float = 0.05,
) -> bool:
    """Test whether a score delta is statistically significant.

    Uses a one-proportion z-test. A delta of 0.03 with 10 samples is
    likely noise; the same delta with 1000 samples is a real signal.

    Args:
        delta: Observed score change (negative = regression).
        n_samples: Number of test cases the scores are averaged over.
        baseline_score: Reference proportion in [0.0, 1.0].
        alpha: Significance level (0.05 → 95 % confidence).

    Returns:
        True if the change is statistically significant at ``alpha`` level.
    """
    if n_samples <= 0:
        return False
    p = max(1e-6, min(1.0 - 1e-6, baseline_score))
    se = math.sqrt(p * (1.0 - p) / n_samples)
    if se < 1e-12:
        return False
    z = abs(delta) / se
    z_crit = _Z_CRITICAL.get(alpha, 1.960)
    return z >= z_crit


class RegressionChecker:
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
