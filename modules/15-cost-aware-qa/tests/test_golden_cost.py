"""Smoke test del golden dataset: verifica que las 100 entradas cargan y son consistentes."""

import json
from pathlib import Path

import pytest

GOLDEN = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "goldens"
    / "15-cost-aware-qa"
    / "cost_records.jsonl"
)


def _load() -> list[dict]:
    with GOLDEN.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


@pytest.fixture(scope="module")
def records() -> list[dict]:
    return _load()


class TestGoldenDataset:
    def test_at_least_100_entries(self, records):
        """Manual §9.2: mínimo 100 entradas para regression gate."""
        assert len(records) >= 100

    def test_all_have_required_fields(self, records):
        required = {
            "model", "tokens_in", "tokens_out", "latency_ms_total",
            "cost_usd", "metadata",
        }
        for r in records:
            assert required.issubset(r.keys())

    def test_stratified_by_query_profile(self, records):
        profiles = {r["query_profile"] for r in records}
        # Esperamos las 5 categorías del generador
        assert len(profiles) == 5

    def test_stratified_by_model(self, records):
        models = {r["model"] for r in records}
        assert len(models) == 5

    def test_cost_is_positive(self, records):
        for r in records:
            assert r["cost_usd"] > 0

    def test_token_counts_realistic(self, records):
        for r in records:
            assert 1 <= r["tokens_in"] <= 10_000
            assert 1 <= r["tokens_out"] <= 5_000
