"""Tests de price_config.py."""

import json

import pytest

from price_config import PRICE_PER_1K, TokenPrice, load_prices_from_config


class TestPricePer1K:
    def test_default_contains_canonical_models(self):
        for model in ("gpt-4o", "gpt-4o-mini", "claude-sonnet-4-5", "claude-haiku-4-5"):
            assert model in PRICE_PER_1K

    def test_prices_are_positive(self):
        for _model, price in PRICE_PER_1K.items():
            assert price.in_per_1k_usd > 0
            assert price.out_per_1k_usd > 0

    def test_out_is_more_expensive_than_in_for_gpt_4o(self):
        p = PRICE_PER_1K["gpt-4o"]
        assert p.out_per_1k_usd > p.in_per_1k_usd

    def test_haiku_cheaper_than_sonnet(self):
        assert PRICE_PER_1K["claude-haiku-4-5"].in_per_1k_usd < PRICE_PER_1K["claude-sonnet-4-5"].in_per_1k_usd


class TestLoadPricesFromConfig:
    def test_none_path_returns_default(self):
        prices = load_prices_from_config(None)
        assert prices == PRICE_PER_1K

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_prices_from_config(tmp_path / "no-existe.json")

    def test_loads_overrides_from_json(self, tmp_path):
        cfg = tmp_path / "prices.json"
        cfg.write_text(json.dumps({"my-model": {"in_per_1k_usd": 0.001, "out_per_1k_usd": 0.002}}))
        prices = load_prices_from_config(cfg)
        assert "my-model" in prices
        assert prices["my-model"] == TokenPrice(0.001, 0.002)
