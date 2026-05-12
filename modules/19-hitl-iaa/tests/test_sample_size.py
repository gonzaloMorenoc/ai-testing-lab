"""Tests de cálculo de tamaño muestral (§31.6)."""

import pytest

from sample_size import EffectSize, n_for_proportion_comparison, recommend_sample_size


class TestRecommendSampleSize:
    def test_large_effect_needs_smallest_sample(self):
        rec = recommend_sample_size(EffectSize.LARGE)
        assert rec.paired_n == 100
        assert rec.unpaired_n == 200

    def test_small_effect_needs_largest_sample(self):
        rec = recommend_sample_size(EffectSize.SMALL)
        assert rec.paired_n >= 1000

    def test_paired_always_smaller_or_equal_than_unpaired(self):
        for es in EffectSize:
            rec = recommend_sample_size(es)
            assert rec.paired_n <= rec.unpaired_n

    def test_rationale_mentions_alpha_and_power(self):
        rec = recommend_sample_size(EffectSize.MEDIUM)
        assert "α=0.05" in rec.rationale
        assert "power" in rec.rationale


class TestProportionComparison:
    def test_larger_effect_needs_smaller_sample(self):
        n_large = n_for_proportion_comparison(0.5, 0.8)  # gran diferencia
        n_small = n_for_proportion_comparison(0.5, 0.55)  # pequeña
        assert n_large < n_small

    def test_returns_positive_integer(self):
        n = n_for_proportion_comparison(0.5, 0.7)
        assert isinstance(n, int) and n > 0

    def test_same_proportion_raises(self):
        with pytest.raises(ValueError, match="distintos"):
            n_for_proportion_comparison(0.5, 0.5)

    def test_higher_power_needs_larger_n(self):
        n_80 = n_for_proportion_comparison(0.5, 0.6, power=0.80)
        n_90 = n_for_proportion_comparison(0.5, 0.6, power=0.90)
        assert n_90 > n_80

    def test_stricter_alpha_needs_larger_n(self):
        n_05 = n_for_proportion_comparison(0.5, 0.6, alpha=0.05)
        n_01 = n_for_proportion_comparison(0.5, 0.6, alpha=0.01)
        assert n_01 > n_05
