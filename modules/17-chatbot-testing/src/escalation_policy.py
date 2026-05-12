"""Política de escalado humano (área 3 del Cap. 10).

Detecta casos donde el bot DEBE derivar a un operador humano:
- Usuario lo solicita explícitamente.
- Tema legal/médico/financiero crítico.
- Frustración detectada (sentiment negativo persistente).
- Bot no entiende tras N intentos.
"""

from __future__ import annotations

from dataclasses import dataclass

CRITICAL_KEYWORDS = [
    "demanda", "abogado", "denuncia", "suicidio", "emergencia",
    "urgente medical", "operador", "humano", "persona real",
]
FRUSTRATION_MARKERS = [
    "no me sirve", "no entiendes", "déjame ya", "es una mierda", "no funciona nada",
]


@dataclass(frozen=True)
class EscalationDecision:
    should_escalate: bool
    reason: str
    confidence: float


def should_escalate(
    user_message: str, conversation_turns: int = 1, failed_intent_attempts: int = 0
) -> EscalationDecision:
    """Decide si escalar a humano. Returns EscalationDecision con motivo."""
    msg = user_message.lower()
    if any(kw in msg for kw in CRITICAL_KEYWORDS):
        return EscalationDecision(True, "critical_keyword_detected", 0.99)
    if any(m in msg for m in FRUSTRATION_MARKERS):
        return EscalationDecision(True, "frustration_detected", 0.85)
    if failed_intent_attempts >= 3:
        return EscalationDecision(True, "repeated_intent_failure", 0.80)
    if conversation_turns >= 10 and failed_intent_attempts >= 2:
        return EscalationDecision(True, "long_conversation_with_failures", 0.70)
    return EscalationDecision(False, "no_escalation_needed", 0.90)


def evaluate_escalation_precision(
    cases: list[tuple[str, bool]],
) -> dict[str, float]:
    """Mide precisión del policy: % casos donde la decisión coincide con la esperada."""
    if not cases:
        return {"precision": 0.0, "n": 0}
    correct = sum(
        1 for msg, expected in cases if should_escalate(msg).should_escalate == expected
    )
    return {"precision": correct / len(cases), "n": len(cases)}
