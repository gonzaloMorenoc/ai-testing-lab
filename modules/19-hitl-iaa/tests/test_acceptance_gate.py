"""Tests de assert_acceptable_iaa (gate de calidad del dataset)."""

import pytest

from iaa_metrics import (
    HIGH_RISK_KAPPA,
    MIN_ACCEPTABLE_KAPPA,
    IAAResult,
    assert_acceptable_iaa,
    cohen_kappa,
)


class TestAcceptanceGate:
    def test_passes_above_min_threshold(self):
        # IAA por encima de 0.667
        result = IAAResult("cohen_kappa", 0.75, "substantial", 50, 2)
        assert_acceptable_iaa(result)  # no raise

    def test_fails_below_min_threshold(self):
        result = IAAResult("cohen_kappa", 0.55, "moderate", 50, 2)
        with pytest.raises(ValueError, match="IAA insuficiente"):
            assert_acceptable_iaa(result)

    def test_high_risk_requires_higher_threshold(self):
        # 0.75 pasa el estándar (>=0.667) pero NO alto riesgo (>=0.80)
        result = IAAResult("cohen_kappa", 0.75, "substantial", 50, 2)
        with pytest.raises(ValueError, match="0.8"):
            assert_acceptable_iaa(result, high_risk=True)

    def test_threshold_constants(self):
        assert MIN_ACCEPTABLE_KAPPA == 0.667
        assert HIGH_RISK_KAPPA == 0.80

    def test_uses_raise_not_assert(self):
        # Manual §28.4: usar raise para sobrevivir python -O
        import inspect

        import iaa_metrics

        src = inspect.getsource(iaa_metrics.assert_acceptable_iaa)
        assert "raise ValueError" in src

    def test_integrates_with_cohen_kappa_pipeline(self):
        # Distribución balanceada con alto acuerdo: 48 de 50 coinciden
        a = ["A"] * 25 + ["B"] * 25
        b = ["A"] * 24 + ["B"] * 1 + ["A"] * 1 + ["B"] * 24
        result = cohen_kappa(a, b)
        # Debe pasar gate estándar (κ esperado > 0.85)
        assert_acceptable_iaa(result)
