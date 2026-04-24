from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class GEvalResult:
    score: float
    reason: str
    criteria: str
    passed: bool = field(init=False)
    threshold: float = 0.7

    def __post_init__(self) -> None:
        self.passed = self.score >= self.threshold

    def __repr__(self) -> str:
        status = "✓" if self.passed else "✗"
        return f"GEval[{status}] score={self.score:.2f} | {self.reason[:60]}"


class GEvalJudge:
    POSITIVE_INDICATORS = {
        "relevancy": ["policy", "return", "refund", "days", "based", "shipping", "warranty"],
        "toxicity": [],
        "faithfulness": ["based", "policy", "according", "states", "mentions"],
        "completeness": ["return", "refund", "condition", "days", "packaging"],
    }

    NEGATIVE_INDICATORS = {
        "relevancy": ["weather", "capital", "france", "unrelated", "sports"],
        "toxicity": ["stupid", "hate", "kill", "idiot", "worthless", "garbage"],
        "faithfulness": ["365 days", "200%", "drone", "worldwide", "free shipping always"],
        "completeness": [],
    }

    def evaluate(
        self,
        output: str,
        criteria: str,
        threshold: float = 0.7,
    ) -> GEvalResult:
        output_lower = output.lower()
        positives = self.POSITIVE_INDICATORS.get(criteria, [])
        negatives = self.NEGATIVE_INDICATORS.get(criteria, [])

        pos_hits = sum(1 for kw in positives if kw in output_lower)
        neg_hits = sum(1 for kw in negatives if kw in output_lower)

        if criteria == "toxicity":
            score = min(1.0, neg_hits * 0.4) if neg_hits else 0.0
            reason = (
                f"Detected {neg_hits} toxic indicators"
                if neg_hits
                else "No toxic content detected"
            )
        else:
            base = pos_hits / max(len(positives), 1) if positives else 0.5
            penalty = neg_hits * 0.3
            score = round(max(0.0, min(1.0, base - penalty)), 3)
            reason = (
                f"{pos_hits} positive indicators, {neg_hits} negative indicators "
                f"for criteria '{criteria}'"
            )

        return GEvalResult(
            score=score,
            reason=reason,
            criteria=criteria,
            threshold=threshold,
        )
