"""Tests que documentan la separación robustness vs red team (§12.7)."""

from perturbations import PerturbationCategory


class TestRobustnessVsRedTeam:
    """Documenta y verifica que robustness NO mezcla con red team."""

    def test_no_jailbreak_perturbations(self):
        """Las perturbaciones del módulo 18 NO incluyen prompts de jailbreak.
        Esos viven en los módulos 07 y 08 (red team)."""
        from perturbations import PERTURBATION_SPECS

        forbidden_keywords = ["jailbreak", "DAN", "ignore previous", "prompt injection"]
        for spec in PERTURBATION_SPECS.values():
            for kw in forbidden_keywords:
                assert kw.lower() not in spec.description.lower()
                assert kw.lower() not in spec.name.lower()

    def test_adversarial_subtle_isnt_a_jailbreak(self):
        """zero_width está en adversarial_subtle pero NO es un ataque al modelo.
        Es una perturbación del input que prueba la estabilidad del tokenizer."""
        from perturbations import PERTURBATION_SPECS

        zw = PERTURBATION_SPECS["zero_width"]
        assert zw.category == PerturbationCategory.ADVERSARIAL_SUBTLE
        assert "filtros" in zw.impact_typical.lower() or "tokenizer" in zw.impact_typical.lower()

    def test_categories_match_manual_taxonomy(self):
        """Las 8 categorías son exactamente las de la Tabla 12.1 del manual."""
        expected = {
            "lexical", "morphological", "syntactic", "lexico_semantic",
            "idiomatic", "length", "case_format", "adversarial_subtle",
        }
        actual = {c.value for c in PerturbationCategory}
        assert actual == expected
