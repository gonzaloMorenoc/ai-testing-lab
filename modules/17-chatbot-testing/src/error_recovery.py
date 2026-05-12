"""Recuperación de errores de tool/API/timeout (área 8 del Cap. 10).

Patrones esperados:
- Retry con backoff exponencial para errores transitorios (5xx, timeout).
- No retry para 4xx (error del cliente).
- Mensaje user-facing apropiado según tipo de error.
- Escalado a humano si fallan N reintentos.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ErrorKind(StrEnum):
    TRANSIENT = "transient"     # 5xx, timeout, rate limit
    CLIENT_ERROR = "client"     # 4xx (no reintentar)
    VALIDATION = "validation"   # input malformado del LLM
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class RecoveryDecision:
    retry: bool
    backoff_seconds: float
    escalate: bool
    user_facing_message: str


def classify_error(status_code: int | None, timeout: bool = False) -> ErrorKind:
    if timeout:
        return ErrorKind.TRANSIENT
    if status_code is None:
        return ErrorKind.UNKNOWN
    if status_code in (408, 429) or status_code >= 500:
        return ErrorKind.TRANSIENT
    if 400 <= status_code < 500:
        return ErrorKind.CLIENT_ERROR
    return ErrorKind.UNKNOWN


def decide_recovery(
    error: ErrorKind, retry_count: int = 0, max_retries: int = 3
) -> RecoveryDecision:
    """Decide acción de recovery según el tipo de error y retry actual."""
    if error == ErrorKind.TRANSIENT and retry_count < max_retries:
        # Backoff exponencial: 1, 2, 4 segundos
        backoff = float(2 ** retry_count)
        return RecoveryDecision(
            retry=True,
            backoff_seconds=backoff,
            escalate=False,
            user_facing_message="Estoy reintentando, dame un momento.",
        )
    if error == ErrorKind.TRANSIENT and retry_count >= max_retries:
        return RecoveryDecision(
            retry=False,
            backoff_seconds=0.0,
            escalate=True,
            user_facing_message="Tengo problemas técnicos persistentes. Te paso con un operador humano.",
        )
    if error == ErrorKind.CLIENT_ERROR:
        return RecoveryDecision(
            retry=False,
            backoff_seconds=0.0,
            escalate=False,
            user_facing_message="No pude completar tu solicitud. ¿Puedes reformularla?",
        )
    if error == ErrorKind.VALIDATION:
        return RecoveryDecision(
            retry=True,
            backoff_seconds=0.0,
            escalate=False,
            user_facing_message="Voy a reformular la consulta interna.",
        )
    return RecoveryDecision(
        retry=False,
        backoff_seconds=0.0,
        escalate=True,
        user_facing_message="Error inesperado. Te paso con un operador.",
    )


def recovery_success_rate(
    decisions: list[tuple[RecoveryDecision, bool]],
) -> float:
    """% de errores donde el bot tomó la decisión correcta (recuperó o escaló bien)."""
    if not decisions:
        return 0.0
    success = sum(1 for decision, outcome in decisions if outcome)
    return success / len(decisions)
