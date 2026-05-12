"""Mock determinista de intent classifier para evaluación.

En producción, esto se reemplaza por Rasa NLU, AWS Lex, Dialogflow CX o un
clasificador BERT/SetFit. La interfaz es la misma: `predict(query) -> intent`.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IntentPrediction:
    intent: str
    confidence: float


# Regla mínima: keyword matching. Es suficiente para tests de la layer superior.
_INTENT_RULES: dict[str, list[str]] = {
    "policy_returns": ["devolución", "devolver", "reembolso", "return"],
    "shipping": ["envío", "envio", "transporte", "shipping", "entrega"],
    "cancel_order": ["cancelar", "cancelación", "cancel"],
    "billing": ["factura", "facturación", "pago", "cobro"],
    "human_support": ["operador", "humano", "persona", "queja", "demanda"],
    "out_of_scope": [],
}


def predict_intent(query: str) -> IntentPrediction:
    """Heurística basada en keywords con confianza decreciente por keyword."""
    q = query.lower()
    best_intent = "out_of_scope"
    best_confidence = 0.0
    for intent, keywords in _INTENT_RULES.items():
        if not keywords:
            continue
        matches = sum(1 for kw in keywords if kw in q)
        if matches > 0:
            conf = min(0.5 + 0.2 * matches, 0.99)
            if conf > best_confidence:
                best_intent = intent
                best_confidence = conf
    return IntentPrediction(intent=best_intent, confidence=best_confidence)


def evaluate_intent_accuracy(
    cases: list[tuple[str, str]],
) -> dict[str, float]:
    """Precisión sobre casos `(query, expected_intent)`."""
    if not cases:
        return {"accuracy": 0.0, "n": 0}
    correct = sum(
        1 for query, expected in cases if predict_intent(query).intent == expected
    )
    return {"accuracy": correct / len(cases), "n": len(cases)}
