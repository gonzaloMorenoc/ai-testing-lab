"""Tests de las 4 métricas de robustness §12.3."""

import pytest

from robustness_metrics import (
    PerturbationResult,
    RobustnessReport,
    accuracy_degradation,
    aggregate_by_segment,
    build_report,
    consistency_score,
    measure,
    refusal_stability,
    semantic_stability,
)


def _result(sim: float, refusal_changed: bool = False) -> PerturbationResult:
    return PerturbationResult(
        original_query="q",
        perturbed_query="q'",
        perturbation_name="any",
        similarity=sim,
        refusal_changed=refusal_changed,
    )


class TestConsistencyScore:
    def test_empty_returns_zero(self):
        assert consistency_score([]) == 0.0

    def test_average_of_similarities(self):
        results = [_result(0.9), _result(0.8), _result(0.7)]
        assert consistency_score(results) == pytest.approx(0.8)

    def test_perfect_consistency(self):
        results = [_result(1.0)] * 10
        assert consistency_score(results) == 1.0


class TestSemanticStability:
    def test_threshold_filter(self):
        results = [_result(0.9), _result(0.5), _result(0.8)]
        # con threshold=0.75 ⇒ 2 de 3 pasan
        assert semantic_stability(results, threshold=0.75) == pytest.approx(2 / 3)

    def test_empty_returns_zero(self):
        assert semantic_stability([]) == 0.0

    def test_all_above_threshold(self):
        results = [_result(0.9) for _ in range(5)]
        assert semantic_stability(results, threshold=0.5) == 1.0


class TestRefusalStability:
    def test_no_refusal_changes_is_perfect(self):
        results = [_result(0.9, refusal_changed=False)] * 5
        assert refusal_stability(results) == 1.0

    def test_partial_changes(self):
        results = [
            _result(0.9, refusal_changed=False),
            _result(0.9, refusal_changed=True),
            _result(0.9, refusal_changed=False),
            _result(0.9, refusal_changed=False),
        ]
        # 3 estables de 4 ⇒ 0.75
        assert refusal_stability(results) == 0.75

    def test_empty_defaults_to_perfect(self):
        assert refusal_stability([]) == 1.0


class TestAccuracyDegradation:
    def test_no_degradation(self):
        assert accuracy_degradation(0.90, 0.90) == 0.0

    def test_positive_degradation(self):
        assert accuracy_degradation(0.90, 0.85) == pytest.approx(0.05)

    def test_negative_when_perturbation_improves(self):
        # Perturbación que mejora ⇒ degradación negativa
        assert accuracy_degradation(0.85, 0.90) < 0


class TestAggregateBySegment:
    def test_by_perturbation_name(self):
        results = [
            PerturbationResult("q", "q'", "uppercase", 0.9, False),
            PerturbationResult("q", "q'", "uppercase", 0.8, False),
            PerturbationResult("q", "q'", "typo", 0.5, False),
        ]
        agg = aggregate_by_segment(results, segment_key=lambda r: r.perturbation_name)
        assert agg["uppercase"] == pytest.approx(0.85)
        assert agg["typo"] == 0.5


class TestBuildReport:
    def test_passing_report(self):
        results = [_result(0.9)] * 10
        report = build_report(results, consistency_target=0.80)
        assert report.passed
        assert report.consistency_score >= 0.80
        assert report.refusal_stability == 1.0

    def test_failing_due_to_low_consistency(self):
        results = [_result(0.5)] * 10
        report = build_report(results, consistency_target=0.80)
        assert not report.passed

    def test_failing_due_to_refusal_instability(self):
        # consistencia alta pero refusal cambia mucho
        results = [_result(0.95, refusal_changed=True)] * 10
        report = build_report(results)
        assert not report.passed

    def test_with_accuracy_pre_post(self):
        results = [_result(0.9)] * 5
        report = build_report(results, accuracy_pre=0.90, accuracy_post=0.88)
        assert report.accuracy_degradation == pytest.approx(0.02)
        assert report.passed

    def test_failing_due_to_accuracy_degradation_too_high(self):
        results = [_result(0.95)] * 5
        report = build_report(results, accuracy_pre=0.90, accuracy_post=0.75)
        # Caída de 15% > umbral 5%
        assert not report.passed


class TestMeasure:
    def test_measure_returns_similarity(self):
        sim = measure("hello world", "hello world")
        assert sim == 1.0

    def test_measure_different_strings(self):
        sim = measure("hello world", "completely different")
        assert sim < 0.3
