from __future__ import annotations

import re
from dataclasses import dataclass

from src.claim_extractor import extract_claims

_MIN_TOKEN_LENGTH = 3

# Tokens that indicate negation — used to detect claim-context contradictions.
_NEGATION_MARKERS: frozenset[str] = frozenset({
    "not", "never", "no", "none", "neither", "nor",
    "cannot", "cant", "doesnt", "isnt", "arent", "wont", "didnt",
    "nothing", "nowhere", "nobody",
})


@dataclass
class GroundednessResult:
    score: float
    total_claims: int
    grounded_claims: int
    ungrounded: list[str]
    threshold: float

    @property
    def passed(self) -> bool:
        return self.score >= self.threshold

    def __repr__(self) -> str:
        status = "✓" if self.passed else "✗"
        return (
            f"Groundedness[{status}] "
            f"{self.grounded_claims}/{self.total_claims} claims grounded "
            f"(score={self.score:.2f})"
        )


class GroundednessChecker:
    def __init__(self, overlap_threshold: float = 0.5) -> None:
        self.overlap_threshold = overlap_threshold

    def _tokenize(self, text: str) -> set[str]:
        cleaned = (re.sub(r'[^a-zA-Z0-9]', '', w) for w in text.split())
        return {w.lower() for w in cleaned if len(w) > _MIN_TOKEN_LENGTH}

    def _has_negation(self, text: str) -> bool:
        raw_words = {re.sub(r"[^a-z]", "", w) for w in text.lower().split()}
        return bool(raw_words & _NEGATION_MARKERS)

    def _is_grounded(self, claim: str, context_tokens: set[str]) -> bool:
        claim_tokens = self._tokenize(claim)
        if not claim_tokens:
            return True

        # Negation guard: if the claim negates a statement the context affirms,
        # it is a contradiction and should be marked ungrounded.
        if self._has_negation(claim.lower()):
            positive_tokens = claim_tokens - _NEGATION_MARKERS
            if positive_tokens:
                pos_overlap = positive_tokens & context_tokens
                pos_ratio = len(pos_overlap) / len(positive_tokens)
                if pos_ratio >= self.overlap_threshold:
                    return False  # claim negates something context affirms

        overlap = claim_tokens & context_tokens
        return len(overlap) / len(claim_tokens) >= self.overlap_threshold

    def check(
        self,
        response: str,
        context: list[str],
        score_threshold: float = 0.7,
    ) -> GroundednessResult:
        if not context:
            return GroundednessResult(
                score=0.0,
                total_claims=0,
                grounded_claims=0,
                ungrounded=[],
                threshold=score_threshold,
            )

        claims = extract_claims(response)
        if not claims:
            return GroundednessResult(
                score=1.0,
                total_claims=0,
                grounded_claims=0,
                ungrounded=[],
                threshold=score_threshold,
            )

        context_tokens = self._tokenize(" ".join(context))
        grounded = [c for c in claims if self._is_grounded(c, context_tokens)]
        ungrounded = [c for c in claims if not self._is_grounded(c, context_tokens)]
        score = round(len(grounded) / len(claims), 3)

        return GroundednessResult(
            score=score,
            total_claims=len(claims),
            grounded_claims=len(grounded),
            ungrounded=ungrounded,
            threshold=score_threshold,
        )
