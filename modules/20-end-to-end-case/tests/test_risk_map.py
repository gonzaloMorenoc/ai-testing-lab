"""Tests del mapa de riesgos D.1."""

import pytest

from risk_map import RISK_MAP, RiskCategory, find_requirement


class TestRiskMap:
    def test_all_categories_present(self):
        risks_in_map = {entry.risk for entry in RISK_MAP}
        assert risks_in_map == set(RiskCategory)

    def test_hallucination_requires_faithfulness_high(self):
        entry = find_requirement(RiskCategory.HALLUCINATION)
        assert "0.90" in entry.qa_requirement

    def test_pii_requires_zero_leaks(self):
        entry = find_requirement(RiskCategory.PII_LEAK)
        assert "0 leaks" in entry.qa_requirement

    def test_injection_requires_owasp_suite(self):
        entry = find_requirement(RiskCategory.PROMPT_INJECTION)
        assert "OWASP" in entry.qa_requirement

    def test_unknown_risk_raises(self):
        with pytest.raises(KeyError):
            find_requirement("nonexistent")  # type: ignore[arg-type]


class TestRiskCategoryEnum:
    def test_six_canonical_categories(self):
        assert len(list(RiskCategory)) == 6
