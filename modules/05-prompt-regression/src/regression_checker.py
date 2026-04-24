from __future__ import annotations

from dataclasses import dataclass


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
