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


class TestHallucinationClassifier:
    """Tests para la taxonomía de alucinaciones (Ji et al. 2023)."""

    from src.hallucination_types import (
        HallucinationClassifier,
        HallucinationLevel1,
        HallucinationLevel2,
        HallucinationReport,
    )

    @pytest.fixture
    def classifier(self) -> TestHallucinationClassifier.HallucinationClassifier:
        from src.hallucination_types import HallucinationClassifier

        return HallucinationClassifier()

    @pytest.fixture
    def base_context(self) -> str:
        return (
            "Our return policy allows customers to return any product within 30 days "
            "of purchase for a full refund."
        )

    # ------------------------------------------------------------------ #
    # has_hallucination                                                    #
    # ------------------------------------------------------------------ #

    def test_no_claims_returns_no_hallucination(
        self, classifier: TestHallucinationClassifier.HallucinationClassifier, base_context: str
    ) -> None:
        from src.hallucination_types import HallucinationReport

        report = classifier.classify(
            response="Returns are allowed within 30 days.",
            context=base_context,
            unsupported_claims=[],
        )
        assert isinstance(report, HallucinationReport)
        assert report.has_hallucination is False
        assert report.passed is True
        assert report.level1 is None
        assert report.level2 is None
        assert report.unsupported_claims == ()
        assert report.confidence == 1.0

    def test_with_claims_returns_hallucination(
        self, classifier: TestHallucinationClassifier.HallucinationClassifier, base_context: str
    ) -> None:
        report = classifier.classify(
            response="We offer a 500% money-back guarantee.",
            context=base_context,
            unsupported_claims=["We offer a 500% money-back guarantee."],
        )
        assert report.has_hallucination is True
        assert report.passed is False
        assert len(report.unsupported_claims) == 1

    def test_report_is_immutable(
        self, classifier: TestHallucinationClassifier.HallucinationClassifier, base_context: str
    ) -> None:
        report = classifier.classify(
            response="Drones deliver within 1 minute.",
            context=base_context,
            unsupported_claims=["Drones deliver within 1 minute."],
        )
        with pytest.raises((AttributeError, TypeError)):
            report.has_hallucination = False  # type: ignore[misc]

    # ------------------------------------------------------------------ #
    # Level 2 — TEMPORAL                                                  #
    # ------------------------------------------------------------------ #

    def test_claim_with_temporal_signal_in_2019(
        self, classifier: TestHallucinationClassifier.HallucinationClassifier, base_context: str
    ) -> None:
        from src.hallucination_types import HallucinationLevel2

        report = classifier.classify(
            response="The policy changed in 2019 to allow 365 days.",
            context=base_context,
            unsupported_claims=["The policy changed in 2019 to allow 365 days."],
        )
        assert report.level2 == HallucinationLevel2.TEMPORAL

    def test_claim_with_recently_signal(
        self, classifier: TestHallucinationClassifier.HallucinationClassifier, base_context: str
    ) -> None:
        from src.hallucination_types import HallucinationLevel2

        report = classifier.classify(
            response="The return window was recently extended.",
            context=base_context,
            unsupported_claims=["recently extended the return window."],
        )
        assert report.level2 == HallucinationLevel2.TEMPORAL

    # ------------------------------------------------------------------ #
    # Level 2 — FACTUAL / CITATION                                        #
    # ------------------------------------------------------------------ #

    def test_claim_without_temporal_falls_back_to_factual(
        self, classifier: TestHallucinationClassifier.HallucinationClassifier, base_context: str
    ) -> None:
        from src.hallucination_types import HallucinationLevel2

        report = classifier.classify(
            response="Drone delivery is free worldwide.",
            context=base_context,
            unsupported_claims=["Drone delivery is free worldwide."],
        )
        assert report.level2 in {HallucinationLevel2.FACTUAL, HallucinationLevel2.CITATION}

    def test_claim_with_citation_marker(
        self, classifier: TestHallucinationClassifier.HallucinationClassifier, base_context: str
    ) -> None:
        from src.hallucination_types import HallucinationLevel2

        report = classifier.classify(
            response="According to the CEO, returns are free forever.",
            context=base_context,
            unsupported_claims=["according to the CEO, returns are free forever."],
        )
        assert report.level2 == HallucinationLevel2.CITATION

    # ------------------------------------------------------------------ #
    # Level 1 — INTRINSIC vs EXTRINSIC                                    #
    # ------------------------------------------------------------------ #

    def test_claim_sharing_context_words_is_intrinsic(
        self, classifier: TestHallucinationClassifier.HallucinationClassifier, base_context: str
    ) -> None:
        from src.hallucination_types import HallucinationLevel1

        # "return" and "refund" appear in the context, so the claim contradicts it.
        report = classifier.classify(
            response="Returns are not allowed and there is no refund.",
            context=base_context,
            unsupported_claims=["Returns are not allowed and there is no refund."],
        )
        assert report.level1 == HallucinationLevel1.INTRINSIC

    def test_claim_with_no_context_overlap_is_extrinsic(
        self, classifier: TestHallucinationClassifier.HallucinationClassifier, base_context: str
    ) -> None:
        from src.hallucination_types import HallucinationLevel1

        # Completely new information not present in the context.
        report = classifier.classify(
            response="Same-day drone delivery is available globally.",
            context=base_context,
            unsupported_claims=["Same-day drone globally available."],
        )
        assert report.level1 == HallucinationLevel1.EXTRINSIC

    # ------------------------------------------------------------------ #
    # confidence                                                           #
    # ------------------------------------------------------------------ #

    def test_confidence_higher_when_both_levels_detected(
        self, classifier: TestHallucinationClassifier.HallucinationClassifier, base_context: str
    ) -> None:
        # A claim that overlaps the context (→ INTRINSIC) and contains a temporal signal.
        report = classifier.classify(
            response="The return policy changed in 2019.",
            context=base_context,
            unsupported_claims=["The return policy changed in 2019."],
        )
        # Both level1 (INTRINSIC, because "return" and "policy" match context)
        # and level2 (TEMPORAL) are detected → confidence == 0.8
        assert report.confidence == 0.8

    def test_unsupported_claims_preserved_in_report(
        self, classifier: TestHallucinationClassifier.HallucinationClassifier, base_context: str
    ) -> None:
        claims = ["Free worldwide shipping.", "Unlimited returns forever."]
        report = classifier.classify(
            response=" ".join(claims),
            context=base_context,
            unsupported_claims=claims,
        )
        assert report.unsupported_claims == tuple(claims)
