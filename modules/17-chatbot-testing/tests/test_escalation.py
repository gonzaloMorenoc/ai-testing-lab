"""Tests de la política de escalado humano (área 3)."""

import pytest

from escalation_policy import evaluate_escalation_precision, should_escalate


class TestShouldEscalate:
    def test_critical_keyword_escalates(self):
        decision = should_escalate("quiero poner una denuncia")
        assert decision.should_escalate
        assert decision.reason == "critical_keyword_detected"

    def test_explicit_human_request_escalates(self):
        decision = should_escalate("quiero hablar con un operador")
        assert decision.should_escalate

    def test_frustration_escalates(self):
        decision = should_escalate("esto no funciona nada, no me sirve")
        assert decision.should_escalate
        assert decision.reason == "frustration_detected"

    def test_repeated_intent_failure_escalates(self):
        decision = should_escalate("¿qué quieres decir?", failed_intent_attempts=3)
        assert decision.should_escalate
        assert "intent" in decision.reason

    def test_normal_message_doesnt_escalate(self):
        decision = should_escalate("¿cuándo llega mi envío?")
        assert not decision.should_escalate

    def test_long_conversation_with_failures_escalates(self):
        decision = should_escalate(
            "no, no, no, eso no",
            conversation_turns=12,
            failed_intent_attempts=2,
        )
        assert decision.should_escalate


class TestEvaluatePrecision:
    def test_perfect_precision(self):
        cases = [
            ("denuncia", True),
            ("envío", False),
            ("operador", True),
        ]
        result = evaluate_escalation_precision(cases)
        assert result["precision"] == 1.0

    def test_partial_precision(self):
        cases = [
            ("denuncia", True),
            ("hola", True),  # nuestro policy NO escalaría → mal etiquetado
        ]
        result = evaluate_escalation_precision(cases)
        assert result["precision"] == 0.5

    def test_empty_returns_zero(self):
        assert evaluate_escalation_precision([])["precision"] == 0.0
