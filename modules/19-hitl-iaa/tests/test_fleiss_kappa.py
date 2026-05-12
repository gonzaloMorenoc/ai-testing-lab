"""Tests de Fleiss κ."""

import pytest

from iaa_metrics import fleiss_kappa


class TestFleissKappa:
    def test_perfect_agreement(self):
        # 5 ítems, 3 anotadores; todos eligen la misma categoría por ítem
        annotations = [["A"] * 3, ["B"] * 3, ["A"] * 3, ["B"] * 3, ["C"] * 3]
        result = fleiss_kappa(annotations)
        assert result.value == pytest.approx(1.0)

    def test_returns_n_items_and_raters(self):
        annotations = [["A", "A", "A"], ["B", "B", "B"]]
        result = fleiss_kappa(annotations)
        assert result.n_items == 2
        assert result.n_annotators == 3

    def test_partial_agreement_positive_kappa(self):
        # Mayoría coincide pero hay desacuerdos
        annotations = [
            ["A", "A", "A"],
            ["A", "A", "B"],
            ["B", "B", "B"],
            ["B", "B", "B"],
            ["A", "B", "A"],
        ]
        result = fleiss_kappa(annotations)
        assert result.value > 0

    def test_requires_at_least_3_raters(self):
        with pytest.raises(ValueError, match="≥ 3 anotadores"):
            fleiss_kappa([["A", "A"], ["B", "B"]])

    def test_inconsistent_rows_raises(self):
        with pytest.raises(ValueError, match="número distinto"):
            fleiss_kappa([["A", "A", "A"], ["B", "B"]])

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="vacía"):
            fleiss_kappa([])
