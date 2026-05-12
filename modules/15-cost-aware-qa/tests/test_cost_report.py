"""Tests de CostReport y assert_cost_budget."""

import pytest

from cost_report import (
    BudgetExceededError,
    CostReport,
    UnknownModelError,
    assert_cost_budget,
)
from price_config import TokenPrice


class TestCostReport:
    def test_cost_usd_for_known_model(self):
        # gpt-4o-mini: 0.00015 in, 0.0006 out
        r = CostReport(model="gpt-4o-mini", tokens_in=1000, tokens_out=500)
        expected = (1000 / 1000) * 0.00015 + (500 / 1000) * 0.0006
        assert r.cost_usd == pytest.approx(expected, rel=1e-6)

    def test_cost_scales_linearly_with_tokens(self):
        r1 = CostReport("gpt-4o", 1000, 1000)
        r2 = CostReport("gpt-4o", 2000, 2000)
        assert r2.cost_usd == pytest.approx(2 * r1.cost_usd, rel=1e-6)

    def test_unknown_model_raises(self):
        r = CostReport(model="modelo-inexistente", tokens_in=100, tokens_out=50)
        with pytest.raises(UnknownModelError):
            _ = r.cost_usd

    def test_zero_tokens_gives_zero_cost(self):
        r = CostReport("gpt-4o", 0, 0)
        assert r.cost_usd == 0.0

    def test_frozen_dataclass(self):
        r = CostReport("gpt-4o", 100, 50)
        with pytest.raises(Exception):  # FrozenInstanceError
            r.model = "otro"  # type: ignore[misc]

    def test_cost_with_custom_prices(self):
        r = CostReport("custom", 1000, 1000)
        prices = {"custom": TokenPrice(0.01, 0.02)}
        assert r.cost_with_prices(prices) == pytest.approx(0.03, rel=1e-6)


class TestAssertCostBudget:
    def test_within_budget_passes(self):
        r = CostReport("gpt-4o-mini", 100, 50)
        # No raises
        assert_cost_budget(r, max_usd=1.0)

    def test_over_budget_raises_runtime_error(self):
        # gpt-4o caro: 0.0025 in + 0.010 out
        r = CostReport("gpt-4o", 10_000, 10_000)  # 0.025 + 0.10 = 0.125 USD
        with pytest.raises(BudgetExceededError, match="Coste USD"):
            assert_cost_budget(r, max_usd=0.05)

    def test_uses_raise_not_assert_to_survive_O_flag(self):
        # Garantiza que la implementación no usa assert (mensaje deja huella)
        import inspect

        import cost_report

        src = inspect.getsource(cost_report.assert_cost_budget)
        assert "raise BudgetExceededError" in src
        # No queremos un `assert ` que se desactivaría con python -O
        assert "    assert " not in src
