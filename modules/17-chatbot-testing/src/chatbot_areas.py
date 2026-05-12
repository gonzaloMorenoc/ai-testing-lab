"""Las 8 áreas operativas de testing de chatbots (Manual v13 §10.2).

Una batería RAGAS por sí sola NO cubre estas dimensiones. Un chatbot productivo
necesita tests específicos para cada una.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ChatbotTestArea(StrEnum):
    INTENT_DETECTION = "intent_detection"
    FALLBACK = "fallback"
    HUMAN_ESCALATION = "human_escalation"
    TONE_PERSONA = "tone_persona"
    MEMORY = "memory"
    SESSION_ISOLATION = "session_isolation"
    LONG_CONVERSATION = "long_conversation"
    ERROR_RECOVERY = "error_recovery"


@dataclass(frozen=True)
class AreaSpec:
    area: ChatbotTestArea
    description: str
    metric: str
    target: float
    min_cases: int


# Tabla 10.2 — Matriz operativa con umbrales objetivo del manual.
AREA_SPECS: dict[ChatbotTestArea, AreaSpec] = {
    ChatbotTestArea.INTENT_DETECTION: AreaSpec(
        ChatbotTestArea.INTENT_DETECTION,
        "Comprensión de la intención del usuario",
        "intent_accuracy",
        0.90,
        20,
    ),
    ChatbotTestArea.FALLBACK: AreaSpec(
        ChatbotTestArea.FALLBACK,
        "Respuesta apropiada ante queries fuera de dominio",
        "correct_fallback_rate",
        0.90,
        20,
    ),
    ChatbotTestArea.HUMAN_ESCALATION: AreaSpec(
        ChatbotTestArea.HUMAN_ESCALATION,
        "Derivación correcta a operador en casos críticos",
        "escalation_precision",
        0.95,
        20,
    ),
    ChatbotTestArea.TONE_PERSONA: AreaSpec(
        ChatbotTestArea.TONE_PERSONA,
        "Consistencia de estilo y voz de marca",
        "tone_score",
        0.80,
        20,
    ),
    ChatbotTestArea.MEMORY: AreaSpec(
        ChatbotTestArea.MEMORY,
        "Recuerdo de información previa de la sesión",
        "context_retention",
        0.85,
        20,
    ),
    ChatbotTestArea.SESSION_ISOLATION: AreaSpec(
        ChatbotTestArea.SESSION_ISOLATION,
        "No contaminación entre usuarios concurrentes",
        "session_isolation",
        1.00,
        10,
    ),
    ChatbotTestArea.LONG_CONVERSATION: AreaSpec(
        ChatbotTestArea.LONG_CONVERSATION,
        "Degradación tras N turnos (memoria deslizante)",
        "long_context_consistency",
        0.80,
        10,
    ),
    ChatbotTestArea.ERROR_RECOVERY: AreaSpec(
        ChatbotTestArea.ERROR_RECOVERY,
        "Manejo de error de tool/API/timeout",
        "recovery_success_rate",
        0.90,
        20,
    ),
}
