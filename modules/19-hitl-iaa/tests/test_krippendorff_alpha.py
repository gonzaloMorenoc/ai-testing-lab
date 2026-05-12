"""Tests de Krippendorff α (nominal)."""

import pytest

from iaa_metrics import krippendorff_alpha_nominal


class TestKrippendorffAlpha:
    def test_perfect_agreement(self):
        annotations = [["A", "A", "A"], ["B", "B", "B"]]
        result = krippendorff_alpha_nominal(annotations)
        assert result.value == pytest.approx(1.0)

    def test_handles_missing_values(self):
        annotations = [["A", "A", None], ["B", None, "B"]]
        result = krippendorff_alpha_nominal(annotations)
        # Suficientes anotaciones presentes; α=1.0 porque los presentes concuerdan
        assert result.value == pytest.approx(1.0)

    def test_returns_zero_when_no_pairs(self):
        # Ítems con menos de 2 anotaciones presentes
        annotations = [["A", None, None], ["B", None, None]]
        result = krippendorff_alpha_nominal(annotations)
        assert result.value == 0.0

    def test_partial_disagreement_below_1(self):
        annotations = [
            ["A", "A", "A"],
            ["A", "B", "A"],
            ["B", "B", "B"],
            ["A", "A", "B"],
        ]
        result = krippendorff_alpha_nominal(annotations)
        assert 0 < result.value < 1

    def test_requires_at_least_2_raters(self):
        with pytest.raises(ValueError, match="≥ 2"):
            krippendorff_alpha_nominal([["A"], ["B"]])

    def test_metric_name(self):
        result = krippendorff_alpha_nominal([["A", "A"], ["B", "B"]])
        assert result.metric == "krippendorff_alpha_nominal"
