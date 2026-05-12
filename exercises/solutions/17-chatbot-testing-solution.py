"""Solución del ejercicio del módulo 17.

Ejercicio: dada una conversación de 3 turnos con un cliente frustrado,
identificar las áreas del Cap. 10 que deben activar pruebas:
- ¿Detecta el intent?
- ¿Escala correctamente cuando hay frustración?
- ¿Mantiene tono formal?

Modo de uso:
    python exercises/solutions/17-chatbot-testing-solution.py
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "modules" / "17-chatbot-testing" / "src"))
sys.path.insert(0, str(REPO))

from escalation_policy import should_escalate  # noqa: E402
from intent_classifier import predict_intent  # noqa: E402
from tone_evaluator import evaluate_tone  # noqa: E402


def main() -> None:
    conversation = [
        ("usuario", "quiero devolver un pedido"),
        ("bot", "Estimado cliente, por favor proporcione su número de pedido. Atentamente."),
        ("usuario", "ya te lo di hace 5 minutos, esto no funciona nada"),
        ("bot", "Lamento la confusión. ¿Podría facilitarme el número nuevamente?"),
        ("usuario", "quiero hablar con un operador humano YA"),
    ]

    last_user_msg = conversation[-1][1]
    intent = predict_intent(last_user_msg)
    decision = should_escalate(
        last_user_msg, conversation_turns=3, failed_intent_attempts=1
    )
    bot_responses = [m for role, m in conversation if role == "bot"]
    tone_scores = [evaluate_tone(r, expected_register="formal").score for r in bot_responses]

    print("=== Análisis de conversación ===")
    print(f"Intent último mensaje: {intent.intent} (conf={intent.confidence:.2f})")
    print(f"Escalar a humano: {decision.should_escalate} ({decision.reason})")
    print(f"Tone scores bot: {tone_scores}")
    print()
    print("Diagnóstico:")
    if decision.should_escalate:
        print("  ✓ Bot debe escalar (frustración + petición explícita)")
    if intent.intent == "human_support":
        print("  ✓ Intent detectado correctamente")
    print(f"  Promedio tono formal: {sum(tone_scores)/len(tone_scores):.2f}")


if __name__ == "__main__":
    main()
