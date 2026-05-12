"""CostReport y assert_cost_budget.

Manual QA AI v13 §27.3 y §28.4: las validaciones de presupuesto en runtime
deben usar `raise`, no `assert`. `assert` se desactiva con `python -O` o
`PYTHONOPTIMIZE=1`, lo que dejaría pasar excesos silenciosos.
"""

from __future__ import annotations

from dataclasses import dataclass

from price_config import PRICE_PER_1K, TokenPrice


class UnknownModelError(KeyError):
    """Modelo no registrado en PRICE_PER_1K."""


class BudgetExceededError(RuntimeError):
    """El coste calculado supera el presupuesto."""


@dataclass(frozen=True)
class CostReport:
    """Reporte inmutable de coste de una query.

    Fields:
        model: id del modelo (debe estar en PRICE_PER_1K).
        tokens_in: tokens de entrada (system + context + user).
        tokens_out: tokens generados por el LLM.
    """

    model: str
    tokens_in: int
    tokens_out: int

    def _price(self, prices: dict[str, TokenPrice] | None = None) -> TokenPrice:
        table = prices if prices is not None else PRICE_PER_1K
        if self.model not in table:
            raise UnknownModelError(self.model)
        return table[self.model]

    @property
    def cost_usd(self) -> float:
        p = self._price()
        return (self.tokens_in / 1000) * p.in_per_1k_usd + (
            self.tokens_out / 1000
        ) * p.out_per_1k_usd

    def cost_with_prices(self, prices: dict[str, TokenPrice]) -> float:
        """Coste calculado con un diccionario de precios distinto al default."""
        p = self._price(prices)
        return (self.tokens_in / 1000) * p.in_per_1k_usd + (
            self.tokens_out / 1000
        ) * p.out_per_1k_usd


def assert_cost_budget(report: CostReport, max_usd: float) -> None:
    """Eleva BudgetExceededError si el coste supera max_usd.

    Usa raise (no assert) para sobrevivir a `python -O` (Manual v13 §28.4).
    """
    if report.cost_usd > max_usd:
        raise BudgetExceededError(
            f"Coste USD {report.cost_usd:.4f} > presupuesto {max_usd:.4f} "
            f"(model={report.model}, in={report.tokens_in}, out={report.tokens_out})"
        )
