"""Tests de chatbot_areas.py — Tabla 10.2 del manual."""

from chatbot_areas import AREA_SPECS, ChatbotTestArea


class TestChatbotAreas:
    def test_eight_areas_present(self):
        assert len(list(ChatbotTestArea)) == 8

    def test_all_specs_have_target_threshold(self):
        for area, spec in AREA_SPECS.items():
            assert 0.0 <= spec.target <= 1.0
            assert spec.area == area

    def test_session_isolation_requires_perfect(self):
        # Aislamiento de sesiones DEBE ser 100 % (no negociable)
        assert AREA_SPECS[ChatbotTestArea.SESSION_ISOLATION].target == 1.00

    def test_escalation_higher_threshold_than_intent(self):
        # Escalar a humano mal es más caro que clasificar intent mal
        esc = AREA_SPECS[ChatbotTestArea.HUMAN_ESCALATION]
        intent = AREA_SPECS[ChatbotTestArea.INTENT_DETECTION]
        assert esc.target > intent.target

    def test_minimum_cases_at_least_10(self):
        for spec in AREA_SPECS.values():
            assert spec.min_cases >= 10
