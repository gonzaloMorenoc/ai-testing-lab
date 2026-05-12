"""Tests del contexto del producto (D.1)."""

from product_setup import DEFAULT_PRODUCT, ProductContext


class TestProductContext:
    def test_canonical_values(self):
        ctx = DEFAULT_PRODUCT
        assert ctx.users == 800
        assert ctx.queries_per_day == 25_000
        assert ctx.primary_llm == "claude-sonnet-4-5"
        assert ctx.classifier_llm == "claude-haiku-4-5"

    def test_three_languages(self):
        assert set(DEFAULT_PRODUCT.countries) == {"ES", "PT", "EN"}

    def test_peak_queries_per_hour(self):
        # 25k/24 = 1042/h baseline; × 4 picos = 4166/h aprox
        peak = DEFAULT_PRODUCT.peak_queries_per_hour()
        assert 3500 <= peak <= 5000

    def test_team_includes_qa_and_security(self):
        roles = set(DEFAULT_PRODUCT.team_roles)
        assert "QAEngineer" in roles
        assert "SecurityLead" in roles

    def test_frozen_dataclass(self):
        import pytest

        with pytest.raises(Exception):
            DEFAULT_PRODUCT.users = 1000  # type: ignore[misc]

    def test_custom_context(self):
        custom = ProductContext(users=200, countries=("ES",), queries_per_day=5_000)
        assert custom.users == 200
        assert custom.countries == ("ES",)
