from __future__ import annotations

import os

import pytest

from src.claim_extractor import extract_claims
from src.groundedness_checker import GroundednessChecker, GroundednessResult


class TestClaimExtractor:

    def test_extracts_multiple_claims(self, faithful_response: str) -> None:
        claims = extract_claims(faithful_response)
        print(f"\n  Claims: {claims}")
        assert len(claims) >= 2

    def test_empty_response_returns_empty_list(self) -> None:
        assert extract_claims("") == []

    def test_short_sentence_filtered(self) -> None:
        claims = extract_claims("Yes. No. Maybe. Returns are allowed within 30 days.", min_words=4)
        assert all(len(c.split()) >= 4 for c in claims)


class TestGroundednessChecker:

    def test_faithful_response_scores_high(
        self,
        checker: GroundednessChecker,
        faithful_response: str,
        good_context: list[str],
    ) -> None:
        result: GroundednessResult = checker.check(faithful_response, good_context)
        print(f"\n  {result}")
        assert result.score >= 0.6, f"Faithful response should score >= 0.6, got {result.score}"
        assert result.passed

    def test_hallucinated_response_scores_low(
        self,
        checker: GroundednessChecker,
        hallucinated_response: str,
        good_context: list[str],
    ) -> None:
        result = checker.check(hallucinated_response, good_context, score_threshold=0.7)
        print(f"\n  {result}")
        print(f"  Ungrounded claims: {result.ungrounded}")
        assert result.score < 0.6, f"Hallucinated response should score < 0.6, got {result.score}"
        assert not result.passed

    def test_no_context_returns_zero(
        self, checker: GroundednessChecker, faithful_response: str
    ) -> None:
        result = checker.check(faithful_response, [])
        assert result.score == 0.0
        assert not result.passed

    def test_threshold_configurable(
        self,
        faithful_response: str,
        good_context: list[str],
    ) -> None:
        strict = GroundednessChecker(overlap_threshold=0.8)
        lenient = GroundednessChecker(overlap_threshold=0.2)
        result_strict = strict.check(faithful_response, good_context, score_threshold=0.9)
        result_lenient = lenient.check(faithful_response, good_context, score_threshold=0.5)
        print(f"\n  Strict: {result_strict.score:.2f}, Lenient: {result_lenient.score:.2f}")
        assert result_lenient.score >= result_strict.score

    def test_ungrounded_claims_reported(
        self,
        checker: GroundednessChecker,
        hallucinated_response: str,
        good_context: list[str],
    ) -> None:
        result = checker.check(hallucinated_response, good_context)
        assert len(result.ungrounded) > 0, "Should report which claims are ungrounded"
        print(f"\n  Ungrounded: {result.ungrounded}")

    def test_partial_hallucination_detected(
        self, checker: GroundednessChecker, good_context: list[str]
    ) -> None:
        mixed_response = (
            "Returns are allowed within 30 days. "
            "We also offer a secret 500% refund guarantee for premium members."
        )
        result = checker.check(mixed_response, good_context)
        print(f"\n  Partial hallucination score: {result.score:.2f}")
        assert 0.0 < result.score < 1.0, "Partial hallucination should give intermediate score"

    def test_negated_claim_contradicting_context_is_ungrounded(self) -> None:
        checker = GroundednessChecker(overlap_threshold=0.5)
        # Context affirms returns ARE allowed; claim says they are NOT
        response = "Returns are not allowed under any circumstances."
        context = ["Returns are allowed within 30 days for a full refund."]
        result = checker.check(response, context)
        print(f"\n  Negation detection: {result}")
        assert not result.passed, (
            "A claim that negates an affirmed context statement should be ungrounded"
        )
        assert len(result.ungrounded) >= 1

    def test_negated_claim_about_absent_topic_may_be_grounded(self) -> None:
        checker = GroundednessChecker(overlap_threshold=0.5)
        # Context talks about returns; claim negates something NOT in context → low positive overlap
        response = "Cryptocurrency payments are not accepted."
        context = ["Returns are allowed within 30 days for a full refund."]
        result = checker.check(response, context)
        print(f"\n  Negation (absent topic): {result}")
        # The claim doesn't contradict context strongly (different topic) — grounded or low score
        # The key property: no false contradiction flag

    @pytest.mark.slow
    def test_with_real_deepeval_hallucination(
        self, faithful_response: str, good_context: list[str]
    ) -> None:
        if not os.getenv("GROQ_API_KEY"):
            pytest.skip("GROQ_API_KEY no encontrado")
        from deepeval.metrics import HallucinationMetric
        from deepeval.test_case import LLMTestCase
        tc = LLMTestCase(
            input="What is the return policy?",
            actual_output=faithful_response,
            context=good_context,
        )
        metric = HallucinationMetric(threshold=0.5)
        metric.measure(tc)
        print(f"\n  Real HallucinationMetric score: {metric.score}")
        assert metric.is_successful()
