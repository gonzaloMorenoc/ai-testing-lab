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

    def compare(
        self,
        output_a: str,
        output_b: str,
        criteria: str,
        threshold: float = 0.7,
    ) -> dict:
        """Score two outputs independently and return which wins."""
        result_a = self.evaluate(output_a, criteria, threshold)
        result_b = self.evaluate(output_b, criteria, threshold)
        if result_a.score > result_b.score:
            winner = "A"
        elif result_b.score > result_a.score:
            winner = "B"
        else:
            winner = "tie"
        return {"score_a": result_a.score, "score_b": result_b.score, "winner": winner}

    def calibrate_for_position_bias(
        self,
        output_a: str,
        output_b: str,
        criteria: str,
        threshold: float = 0.7,
    ) -> dict:
        """Detect and correct position bias by evaluating the pair in both orders.

        Standard practice: score [A vs B] and [B vs A], then average.
        A large ``bias_delta`` indicates the judge is order-sensitive.

        Returns:
            calibrated_score_a: A's score averaged across both orderings.
            calibrated_score_b: B's score averaged across both orderings.
            bias_delta: Absolute change in A's score when order is swapped.
            bias_detected: True when bias_delta > 0.05.
            calibrated_winner: Winner based on calibrated scores.
        """
        forward = self.compare(output_a, output_b, criteria, threshold)
        backward = self.compare(output_b, output_a, criteria, threshold)

        # In the backward evaluation, score_a is actually B's score (it was first)
        calibrated_a = round((forward["score_a"] + backward["score_b"]) / 2, 4)
        calibrated_b = round((forward["score_b"] + backward["score_a"]) / 2, 4)
        bias_delta = round(abs(forward["score_a"] - backward["score_b"]), 4)

        if calibrated_a > calibrated_b:
            winner = "A"
        elif calibrated_b > calibrated_a:
            winner = "B"
        else:
            winner = "tie"

        return {
            "calibrated_score_a": calibrated_a,
            "calibrated_score_b": calibrated_b,
            "bias_delta": bias_delta,
            "bias_detected": bias_delta > 0.05,
            "calibrated_winner": winner,
        }
