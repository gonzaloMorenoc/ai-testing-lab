"""Tests del intent classifier (área 1)."""

import pytest

from intent_classifier import IntentPrediction, evaluate_intent_accuracy, predict_intent


class TestPredictIntent:
    def test_returns_intent_prediction(self):
        pred = predict_intent("quiero una devolución")
        assert isinstance(pred, IntentPrediction)

    @pytest.mark.parametrize(
        "query,expected",
        [
            ("quiero una devolución", "policy_returns"),
            ("¿cuándo llega el envío?", "shipping"),
            ("cancelar mi pedido", "cancel_order"),
            ("dame mi factura", "billing"),
            ("quiero hablar con un humano", "human_support"),
            ("hola, ¿cómo estás?", "out_of_scope"),
        ],
    )
    def test_keyword_routing(self, query, expected):
        assert predict_intent(query).intent == expected

    def test_confidence_higher_with_more_matches(self):
        single = predict_intent("envio")
        double = predict_intent("¿cuándo llega el envío con transporte?")
        assert double.confidence >= single.confidence


class TestEvaluateAccuracy:
    def test_empty_cases(self):
        result = evaluate_intent_accuracy([])
        assert result["accuracy"] == 0.0
        assert result["n"] == 0

    def test_all_correct_gives_1(self):
        cases = [
            ("quiero una devolución", "policy_returns"),
            ("cancelar mi pedido", "cancel_order"),
        ]
        result = evaluate_intent_accuracy(cases)
        assert result["accuracy"] == 1.0
        assert result["n"] == 2

    def test_partial_correct(self):
        cases = [
            ("quiero una devolución", "policy_returns"),  # ok
            ("hola", "policy_returns"),  # wrong
        ]
        result = evaluate_intent_accuracy(cases)
        assert result["accuracy"] == 0.5
