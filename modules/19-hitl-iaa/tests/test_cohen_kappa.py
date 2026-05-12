"""Tests de Cohen κ."""

import pytest

from iaa_metrics import IAAResult, cohen_kappa, interpret_kappa


class TestCohenKappa:
    def test_perfect_agreement_returns_1(self):
        a = ["si", "no", "si", "si", "no"]
        result = cohen_kappa(a, a)
        assert result.value == pytest.approx(1.0)
        assert result.interpretation == "almost_perfect"

    def test_no_agreement_returns_negative(self):
        # Anotadores opuestos en todo: κ < 0
        a = ["si", "no", "si", "no"]
        b = ["no", "si", "no", "si"]
        result = cohen_kappa(a, b)
        assert result.value < 0
        assert result.interpretation == "worse_than_chance"

    def test_partial_agreement(self):
        # 8 de 10 acuerdan ⇒ p_o = 0.8
        a = ["A"] * 5 + ["B"] * 5
        b = ["A"] * 4 + ["B"] * 1 + ["A"] * 1 + ["B"] * 4
        result = cohen_kappa(a, b)
        # κ debería ser positivo (acuerdo > azar)
        assert result.value > 0.4

    def test_single_category_degenerate_returns_1(self):
        a = ["only_class"] * 10
        b = ["only_class"] * 10
        result = cohen_kappa(a, b)
        assert result.value == 1.0

    def test_unequal_length_raises(self):
        with pytest.raises(ValueError, match="Longitudes distintas"):
            cohen_kappa(["si"], ["si", "no"])

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="vacías"):
            cohen_kappa([], [])

    def test_returns_iaa_result(self):
        result = cohen_kappa(["a"], ["a"])
        assert isinstance(result, IAAResult)
        assert result.metric == "cohen_kappa"
        assert result.n_annotators == 2
        assert result.n_items == 1


class TestInterpretKappa:
    @pytest.mark.parametrize(
        "kappa,expected",
        [
            (-0.1, "worse_than_chance"),
            (0.1, "poor"),
            (0.30, "fair"),
            (0.55, "moderate"),
            (0.70, "substantial"),
            (0.85, "almost_perfect"),
            (1.0, "almost_perfect"),
        ],
    )
    def test_landis_koch_thresholds(self, kappa, expected):
        assert interpret_kappa(kappa) == expected
