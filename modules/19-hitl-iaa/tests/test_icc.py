"""Tests de ICC(2,1)."""

import pytest

from iaa_metrics import icc_2way_random


class TestICC:
    def test_perfect_agreement_continuous(self):
        # Cada ítem con la misma puntuación entre anotadores
        ratings = [[3.0, 3.0, 3.0], [4.5, 4.5, 4.5], [2.0, 2.0, 2.0]]
        result = icc_2way_random(ratings)
        assert result.value >= 0.95
        assert result.interpretation == "excellent"

    def test_high_variability_low_icc(self):
        # Anotadores no concuerdan en absoluto
        ratings = [[1.0, 5.0, 3.0], [2.0, 4.0, 1.0], [5.0, 1.0, 4.0]]
        result = icc_2way_random(ratings)
        assert result.value < 0.6

    def test_clipped_to_zero(self):
        # Caso degenerado: todas las puntuaciones iguales ⇒ ICC indeterminado, devolvemos 0
        ratings = [[3.0, 3.0], [3.0, 3.0]]
        result = icc_2way_random(ratings)
        assert 0 <= result.value <= 1

    def test_requires_at_least_2_raters(self):
        with pytest.raises(ValueError, match="≥ 2"):
            icc_2way_random([[3.0]])

    def test_inconsistent_rows_raises(self):
        with pytest.raises(ValueError, match="número distinto"):
            icc_2way_random([[3.0, 4.0], [5.0]])

    def test_metric_name(self):
        ratings = [[1.0, 2.0], [3.0, 4.0]]
        result = icc_2way_random(ratings)
        assert result.metric == "icc_2way_random"
