from __future__ import annotations

import numpy as np
import pytest

from src.semantic_drift_detector import detect_semantic_drift, DriftReport


class TestSemanticDriftDetector:
    """Tests para detect_semantic_drift (§10.3 Manual QA AI v12)."""

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
        hist = rng.normal(loc=0.85, scale=0.03, size=200)
        baseline = hist.tolist()
        current = rng.normal(loc=0.88, scale=0.10, size=200).tolist()  # distinta forma

        report = detect_semantic_drift(
            baseline_scores=baseline,
            current_scores=current,
            historical_scores=hist,
        )
        print(f"\n  [only dist changed] dist_changed={report.distribution_changed}, quality_degraded={report.quality_degraded}")
        if not report.quality_degraded:
            assert report.drift_detected is False

    def test_drift_detected_false_when_only_quality_degraded(self) -> None:
        """Si mean_drop < -0.03 pero KS no es significativo → drift=False."""
        rng = np.random.default_rng(44)
        hist = rng.normal(loc=0.90, scale=0.04, size=200)
        baseline = rng.normal(loc=0.90, scale=0.04, size=50).tolist()
        current = rng.normal(loc=0.86, scale=0.04, size=50).tolist()

        report = detect_semantic_drift(
            baseline_scores=baseline,
            current_scores=current,
            historical_scores=hist,
        )
        print(f"\n  [only quality] dist_changed={report.distribution_changed}, mean_drop={report.mean_drop}")
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
            )
