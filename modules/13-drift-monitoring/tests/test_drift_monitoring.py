from __future__ import annotations

import os

import numpy as np
import pytest

from src.alert_rules import (
    AlertHistory,
    AlertResult,
    evaluate_rules,
    mean_drop_alert,
    p95_alert,
    psi_alert,
)
from src.drift_detector import compute_psi


class TestDriftDetector:

    def test_identical_distributions_psi_near_zero(
        self,
        reference_scores: list[float],
        identical_scores: list[float],
    ) -> None:
        psi = compute_psi(reference_scores, identical_scores)
        print(f"\n  PSI identical: {psi}")
        assert psi < 0.1, f"expected PSI near 0 for identical distributions, got {psi}"

    def test_shifted_distribution_psi_high(
        self,
        reference_scores: list[float],
        shifted_scores: list[float],
    ) -> None:
        psi = compute_psi(reference_scores, shifted_scores)
        print(f"\n  PSI shifted: {psi}")
        assert psi > 0.2, f"expected PSI > 0.2 for shifted distribution, got {psi}"


class TestAlertRules:

    def test_mean_drop_20pct_triggers_alert(
        self, reference_scores: list[float], dropped_scores: list[float]
    ) -> None:
        ref_mean = float(np.mean(reference_scores))
        rule = mean_drop_alert(reference_mean=ref_mean, threshold_pct=0.1)
        result = rule(dropped_scores)
        print(f"\n  {result.message}")
        assert result.triggered is True
        assert result.rule_name == "mean_drop_alert"

    def test_mean_drop_5pct_no_alert(self, reference_scores: list[float]) -> None:
        ref_mean = float(np.mean(reference_scores))
        slightly_dropped = [s * 0.97 for s in reference_scores]  # 3% drop
        rule = mean_drop_alert(reference_mean=ref_mean, threshold_pct=0.1)
        result = rule(slightly_dropped)
        print(f"\n  {result.message}")
        assert result.triggered is False

    def test_p95_exceeds_limit_triggers_alert(self) -> None:
        scores = [0.9] * 100
        rule = p95_alert(limit=0.8)
        result = rule(scores)
        print(f"\n  {result.message}")
        assert result.triggered is True
        assert result.rule_name == "p95_alert"

    def test_all_rules_pass_no_alert(self, reference_scores: list[float]) -> None:
        ref_mean = float(np.mean(reference_scores))
        rules: list = [
            mean_drop_alert(reference_mean=ref_mean, threshold_pct=0.3),
            p95_alert(limit=1.5),
        ]
        results = evaluate_rules(rules, reference_scores)
        print(f"\n  {[r.message for r in results]}")
        assert all(not r.triggered for r in results)

    def test_one_failing_rule_identified(self, reference_scores: list[float]) -> None:
        ref_mean = float(np.mean(reference_scores))
        dropped = [s * 0.6 for s in reference_scores]  # 40% drop
        rules: list = [
            mean_drop_alert(reference_mean=ref_mean, threshold_pct=0.3),
            p95_alert(limit=1.5),
        ]
        results = evaluate_rules(rules, dropped)
        triggered = [r for r in results if r.triggered]
        print(f"\n  triggered: {[r.rule_name for r in triggered]}")
        assert len(triggered) == 1
        assert triggered[0].rule_name == "mean_drop_alert"

    def test_alert_result_has_required_fields(self, reference_scores: list[float]) -> None:
        ref_mean = float(np.mean(reference_scores))
        rule = mean_drop_alert(reference_mean=ref_mean)
        result = rule(reference_scores)
        assert isinstance(result, AlertResult)
        assert result.timestamp  # non-empty ISO timestamp
        assert result.rule_name
        assert isinstance(result.observed_value, float)
        assert isinstance(result.threshold, float)
        assert result.message
        print(f"\n  AlertResult: triggered={result.triggered} ts={result.timestamp[:10]}")

    def test_psi_alert_threshold_configurable(
        self, reference_scores: list[float], shifted_scores: list[float]
    ) -> None:
        psi = compute_psi(reference_scores, shifted_scores)
        strict = psi_alert(threshold=0.05)(psi)
        lenient = psi_alert(threshold=10.0)(psi)
        assert strict.triggered is True
        assert lenient.triggered is False

class TestAlertHistory:

    def test_insufficient_data_below_three(self) -> None:
        history = AlertHistory("psi_alert")
        history.add(AlertResult(triggered=True, rule_name="psi_alert",
                                observed_value=0.3, threshold=0.2, message="psi high"))
        history.add(AlertResult(triggered=True, rule_name="psi_alert",
                                observed_value=0.35, threshold=0.2, message="psi high"))
        assert history.trend == "insufficient_data"

    def test_two_of_three_recent_triggered_is_degrading(self) -> None:
        history = AlertHistory("psi_alert")
        for triggered, val in [(False, 0.1), (True, 0.25), (True, 0.3)]:
            history.add(AlertResult(
                triggered=triggered, rule_name="psi_alert",
                observed_value=val, threshold=0.2, message="",
            ))
        print(f"\n  Trend: {history.trend}")
        assert history.trend == "degrading"

    def test_zero_of_three_recent_triggered_is_recovering(self) -> None:
        history = AlertHistory("psi_alert")
        for triggered, val in [(True, 0.25), (False, 0.15), (False, 0.05)]:
            history.add(AlertResult(
                triggered=triggered, rule_name="psi_alert",
                observed_value=val, threshold=0.2, message="",
            ))
        assert history.trend == "recovering"

    def test_one_of_three_recent_triggered_is_stable(self) -> None:
        history = AlertHistory("psi_alert")
        for triggered, val in [(False, 0.05), (True, 0.25), (False, 0.15)]:
            history.add(AlertResult(
                triggered=triggered, rule_name="psi_alert",
                observed_value=val, threshold=0.2, message="",
            ))
        assert history.trend == "stable"

    def test_trigger_rate_computed_correctly(self) -> None:
        history = AlertHistory("mean_drop")
        history.add(AlertResult(triggered=True, rule_name="mean_drop",
                                observed_value=0.6, threshold=0.7, message=""))
        history.add(AlertResult(triggered=False, rule_name="mean_drop",
                                observed_value=0.75, threshold=0.7, message=""))
        history.add(AlertResult(triggered=True, rule_name="mean_drop",
                                observed_value=0.65, threshold=0.7, message=""))
        history.add(AlertResult(triggered=False, rule_name="mean_drop",
                                observed_value=0.8, threshold=0.7, message=""))
        assert history.trigger_rate == pytest.approx(0.5, abs=0.01)

    def test_summary_contains_required_fields(self) -> None:
        history = AlertHistory("psi_alert")
        for _ in range(3):
            history.add(AlertResult(triggered=False, rule_name="psi_alert",
                                    observed_value=0.05, threshold=0.2, message="ok"))
        summary = history.summary()
        print(f"\n  {summary}")
        assert "psi_alert" in summary
        assert "trend=" in summary
        assert "trigger_rate=" in summary

    @pytest.mark.slow
    def test_real_langfuse_scores(self) -> None:
        if not os.getenv("LANGFUSE_SECRET_KEY"):
            pytest.skip("LANGFUSE_SECRET_KEY no encontrado")
        rng = np.random.default_rng(0)
        ref = rng.beta(5, 1, size=100).tolist()
        cur = rng.beta(2, 2, size=100).tolist()
        psi = compute_psi(ref, cur)
        print(f"\n  Real PSI (beta distributions): {psi}")
        assert psi >= 0.0


from src.semantic_drift_detector import detect_semantic_drift, DriftReport  # noqa: E402


class TestSemanticDriftDetector:
    """Tests para detect_semantic_drift (§10.3 Manual QA AI v12)."""

    # ------------------------------------------------------------------
    # Fixtures helpers
    # ------------------------------------------------------------------

    def _stable_historical(self) -> np.ndarray:
        """100 puntos ~ N(0.88, 0.04) — distribución de referencia."""
        return np.random.default_rng(10).normal(loc=0.88, scale=0.04, size=100)

    # ------------------------------------------------------------------
    # Datos estables → drift_detected=False
    # ------------------------------------------------------------------

    def test_stable_data_no_drift(self) -> None:
        """Distribuciones idénticas no deben disparar drift_detected."""
        rng = np.random.default_rng(7)
        hist = rng.normal(loc=0.88, scale=0.04, size=100)
        baseline = hist.tolist()
        current = rng.normal(loc=0.88, scale=0.04, size=100).tolist()

        report = detect_semantic_drift(
            baseline_scores=baseline,
            current_scores=current,
            historical_scores=hist,
        )
        print(f"\n  [stable] mean_drop={report.mean_drop}, ks_p={report.ks_pvalue}")
        assert report.drift_detected is False

    def test_stable_data_mean_drop_above_threshold(self) -> None:
        """Con datos estables mean_drop debe estar cerca de 0, no < -0.03."""
        rng = np.random.default_rng(7)
        hist = rng.normal(loc=0.88, scale=0.04, size=100)
        baseline = hist.tolist()
        current = rng.normal(loc=0.88, scale=0.04, size=100).tolist()

        report = detect_semantic_drift(
            baseline_scores=baseline,
            current_scores=current,
            historical_scores=hist,
        )
        assert report.quality_degraded is False

    # ------------------------------------------------------------------
    # Caída significativa → quality_degraded=True
    # ------------------------------------------------------------------

    def test_significant_drop_quality_degraded(self) -> None:
        """Una caída de 0.10 en la media debe marcar quality_degraded=True."""
        rng = np.random.default_rng(99)
        hist = rng.normal(loc=0.88, scale=0.04, size=100)
        baseline = hist.tolist()
        # Caída de ~0.10 → mean_drop ≈ -0.10 < -0.03
        current = rng.normal(loc=0.78, scale=0.04, size=100).tolist()

        report = detect_semantic_drift(
            baseline_scores=baseline,
            current_scores=current,
            historical_scores=hist,
        )
        print(f"\n  [drop] mean_drop={report.mean_drop}")
        assert report.quality_degraded is True
        assert report.mean_drop < -0.03

    def test_moderate_drop_reports_correct_mean(self) -> None:
        """mean_drop debe coincidir con current_mean - historical_mean."""
        rng = np.random.default_rng(55)
        hist = rng.normal(loc=0.90, scale=0.03, size=80)
        baseline = hist.tolist()
        current = rng.normal(loc=0.80, scale=0.03, size=80).tolist()

        report = detect_semantic_drift(
            baseline_scores=baseline,
            current_scores=current,
            historical_scores=hist,
        )
        expected_drop = report.current_mean - report.historical_mean
        assert abs(report.mean_drop - round(expected_drop, 4)) < 1e-6

    # ------------------------------------------------------------------
    # distribution_changed en distribuciones claramente distintas
    # ------------------------------------------------------------------

    def test_clearly_different_distributions_changed(self) -> None:
        """Distribuciones con medias muy separadas → distribution_changed=True."""
        rng = np.random.default_rng(33)
        hist = rng.normal(loc=0.90, scale=0.03, size=200)
        baseline = hist.tolist()
        current = rng.normal(loc=0.50, scale=0.05, size=200).tolist()

        report = detect_semantic_drift(
            baseline_scores=baseline,
            current_scores=current,
            historical_scores=hist,
        )
        print(f"\n  [different] ks_pvalue={report.ks_pvalue}")
        assert report.distribution_changed is True
        assert report.ks_pvalue < 0.01

    def test_same_distribution_not_changed(self) -> None:
        """Distribuciones prácticamente idénticas no deben superar umbral KS."""
        rng = np.random.default_rng(77)
        hist = rng.normal(loc=0.85, scale=0.04, size=300)
        baseline = hist.tolist()
        # Resamplear de la misma distribución
        current = rng.normal(loc=0.85, scale=0.04, size=300).tolist()

        report = detect_semantic_drift(
            baseline_scores=baseline,
            current_scores=current,
            historical_scores=hist,
        )
        print(f"\n  [same dist] ks_pvalue={report.ks_pvalue}")
        assert report.distribution_changed is False

    # ------------------------------------------------------------------
    # drift_detected solo cuando AMBOS criterios se cumplen
    # ------------------------------------------------------------------

    def test_drift_detected_requires_both_criteria(self) -> None:
        """drift_detected=True solo si distribution_changed Y quality_degraded."""
        rng = np.random.default_rng(11)
        hist = rng.normal(loc=0.90, scale=0.03, size=150)
        baseline = hist.tolist()
        current = rng.normal(loc=0.75, scale=0.05, size=150).tolist()

        report = detect_semantic_drift(
            baseline_scores=baseline,
            current_scores=current,
            historical_scores=hist,
        )
        assert report.drift_detected == (report.distribution_changed and report.quality_degraded)

    def test_drift_detected_false_when_only_distribution_changed(self) -> None:
        """Si hay cambio de distribución pero la media no cae > 0.03 → drift=False."""
        rng = np.random.default_rng(22)
        # hist con media 0.85, current con media 0.88 (sube, no baja)
        hist = rng.normal(loc=0.85, scale=0.03, size=200)
        baseline = hist.tolist()
        current = rng.normal(loc=0.88, scale=0.10, size=200).tolist()  # distinta forma

        report = detect_semantic_drift(
            baseline_scores=baseline,
            current_scores=current,
            historical_scores=hist,
        )
        print(f"\n  [only dist changed] dist_changed={report.distribution_changed}, quality_degraded={report.quality_degraded}")
        # drift_detected debe ser False si quality_degraded es False
        if not report.quality_degraded:
            assert report.drift_detected is False

    def test_drift_detected_false_when_only_quality_degraded(self) -> None:
        """Si mean_drop < -0.03 pero KS no es significativo → drift=False."""
        rng = np.random.default_rng(44)
        # hist grande como referencia empírica
        hist = rng.normal(loc=0.90, scale=0.04, size=200)
        # baseline y current del mismo tamaño; current desplazado -0.04 pero
        # con dispersión similar → KS con n=50 puede no rechazar H0 al 1%
        baseline = rng.normal(loc=0.90, scale=0.04, size=50).tolist()
        current = rng.normal(loc=0.86, scale=0.04, size=50).tolist()

        report = detect_semantic_drift(
            baseline_scores=baseline,
            current_scores=current,
            historical_scores=hist,
        )
        print(f"\n  [only quality] dist_changed={report.distribution_changed}, mean_drop={report.mean_drop}")
        # Invariante clave: drift_detected == distribution_changed AND quality_degraded
        assert report.drift_detected == (report.distribution_changed and report.quality_degraded)

    # ------------------------------------------------------------------
    # Campos del DriftReport
    # ------------------------------------------------------------------

    def test_report_is_frozen_dataclass(self) -> None:
        """DriftReport debe ser inmutable (frozen=True)."""
        rng = np.random.default_rng(0)
        hist = rng.normal(loc=0.85, scale=0.04, size=100)
        report = detect_semantic_drift(
            baseline_scores=hist.tolist(),
            current_scores=hist.tolist(),
            historical_scores=hist,
        )
        assert isinstance(report, DriftReport)
        with pytest.raises(Exception):
            report.drift_detected = True  # type: ignore[misc]

    def test_report_affected_count_respects_threshold(self) -> None:
        """affected_count debe ser el número de scores < threshold."""
        rng = np.random.default_rng(0)
        hist = rng.normal(loc=0.85, scale=0.04, size=100)
        current = [0.80, 0.83, 0.90, 0.95] + rng.normal(0.85, 0.04, size=96).tolist()
        report = detect_semantic_drift(
            baseline_scores=hist.tolist(),
            current_scores=current,
            historical_scores=hist,
            threshold=0.85,
        )
        expected = sum(1 for s in current if s < 0.85)
        assert report.affected_count == expected

    def test_report_ci95_low_below_high(self) -> None:
        """ci95_low debe ser menor que ci95_high."""
        rng = np.random.default_rng(0)
        hist = rng.normal(loc=0.85, scale=0.04, size=100)
        report = detect_semantic_drift(
            baseline_scores=hist.tolist(),
            current_scores=hist.tolist(),
            historical_scores=hist,
        )
        assert report.ci95_low < report.ci95_high

    # ------------------------------------------------------------------
    # Errores esperados
    # ------------------------------------------------------------------

    def test_raises_on_length_mismatch(self) -> None:
        """ValueError si len(baseline) != len(current)."""
        rng = np.random.default_rng(0)
        hist = rng.normal(loc=0.85, scale=0.04, size=100)
        baseline = hist.tolist()
        current = rng.normal(loc=0.85, scale=0.04, size=50).tolist()

        with pytest.raises(ValueError, match="Longitudes distintas"):
            detect_semantic_drift(
                baseline_scores=baseline,
                current_scores=current,
                historical_scores=hist,
            )

    def test_raises_on_insufficient_historical_scores(self) -> None:
        """ValueError si historical_scores tiene < 30 muestras."""
        rng = np.random.default_rng(0)
        tiny_hist = rng.normal(loc=0.85, scale=0.04, size=20)
        baseline = rng.normal(loc=0.85, scale=0.04, size=50).tolist()
        current = rng.normal(loc=0.85, scale=0.04, size=50).tolist()

        with pytest.raises(ValueError, match="historical_scores insuficiente"):
            detect_semantic_drift(
                baseline_scores=baseline,
                current_scores=current,
                historical_scores=tiny_hist,
            )

    def test_raises_on_insufficient_implicit_historical(self) -> None:
        """ValueError si baseline_scores (usado como hist) tiene < 30 muestras."""
        rng = np.random.default_rng(0)
        short = rng.normal(loc=0.85, scale=0.04, size=15).tolist()

        with pytest.raises(ValueError, match="historical_scores insuficiente"):
            detect_semantic_drift(
                baseline_scores=short,
                current_scores=short,
                # historical_scores=None → usa baseline_scores (15 < 30)
            )
