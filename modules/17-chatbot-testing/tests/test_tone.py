"""Tests de evaluación de tono (área 4)."""

from tone_evaluator import evaluate_tone, tone_consistency


class TestEvaluateTone:
    def test_formal_polite_response(self):
        result = evaluate_tone(
            "Estimado cliente, por favor encuentre la información solicitada. Atentamente.",
            expected_register="formal",
        )
        assert result.formal
        assert result.polite

    def test_informal_text_doesnt_count_as_formal(self):
        result = evaluate_tone("Hey tío, mira esto.", expected_register="formal")
        assert not result.formal

    def test_empathy_marker_detected(self):
        result = evaluate_tone(
            "Entiendo la situación, lamento mucho lo que le ha pasado.",
            expected_register="formal",
        )
        assert result.empathetic

    def test_rude_text_not_polite(self):
        result = evaluate_tone("Cállate, no me molestes con eso.")
        assert not result.polite


class TestToneConsistency:
    def test_empty_responses_returns_zero(self):
        assert tone_consistency([]) == 0.0

    def test_all_formal_polite_high_score(self):
        responses = [
            "Estimado usuario, por favor, encuentre la información. Atentamente.",
            "Estimado, lamento la espera. Por favor disculpe.",
        ]
        score = tone_consistency(responses, expected_register="formal")
        assert score > 0.5

    def test_mixed_drops_average(self):
        responses = [
            "Estimado, por favor disculpe.",
            "ey tío, no sé",
        ]
        score = tone_consistency(responses, expected_register="formal")
        assert score < 0.6
