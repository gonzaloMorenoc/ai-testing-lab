from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class TraceRecord:
    """15 campos mandatorios de Tabla 16.1 (Manual QA AI v12, Cap 16)."""

    # Identidad
    request_id: str
    user_segment: str

    # Modelo
    model_id: str
    model_version: str

    # Prompt
    prompt_id: str
    prompt_version: str

    # Retriever (RAG)
    retriever_id: str
    retriever_version: str
    top_k_docs: int
    reranker_scores: tuple[float, ...]

    # Respuesta
    response: str
    tokens_in: int
    tokens_out: int
    latency_ms: float

    # Seguridad / Privacidad
    safety_flags: tuple[str, ...]
    pii_flags: tuple[str, ...]

    # Herramientas (agentes)
    tool_calls: tuple[str, ...]

    # Error tracking
    error_code: str | None
    retry_count: int

    # Evaluación
    eval_scores: dict[str, float]


@dataclass(frozen=True)
class TraceValidationError(Exception):
    field: str
    reason: str


def make_trace_record(
    response: str,
    tokens_in: int,
    tokens_out: int,
    latency_ms: float,
    *,
    request_id: str | None = None,
    user_segment: str = "default",
    model_id: str = "unknown",
    model_version: str = "unknown",
    prompt_id: str = "default",
    prompt_version: str = "v1.0",
    retriever_id: str = "none",
    retriever_version: str = "1.0",
    top_k_docs: int = 0,
    reranker_scores: tuple[float, ...] = (),
    safety_flags: tuple[str, ...] = (),
    pii_flags: tuple[str, ...] = (),
    tool_calls: tuple[str, ...] = (),
    error_code: str | None = None,
    retry_count: int = 0,
    eval_scores: dict[str, float] | None = None,
) -> TraceRecord:
    """Crea un TraceRecord con defaults razonables para testing."""
    return TraceRecord(
        request_id=uuid.uuid4().hex if request_id is None else request_id,
        user_segment=user_segment,
        model_id=model_id,
        model_version=model_version,
        prompt_id=prompt_id,
        prompt_version=prompt_version,
        retriever_id=retriever_id,
        retriever_version=retriever_version,
        top_k_docs=top_k_docs,
        reranker_scores=reranker_scores,
        response=response,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        latency_ms=latency_ms,
        safety_flags=safety_flags,
        pii_flags=pii_flags,
        tool_calls=tool_calls,
        error_code=error_code,
        retry_count=retry_count,
        eval_scores=eval_scores if eval_scores is not None else {},
    )


def validate_trace(record: TraceRecord) -> list[TraceValidationError]:
    """Valida que un TraceRecord cumple los requisitos mínimos.

    Reglas:
    - request_id no puede ser vacío
    - tokens_in >= 0
    - tokens_out >= 0
    - latency_ms >= 0
    - retry_count >= 0
    - top_k_docs >= 0
    - eval_scores values deben estar en [0, 1]

    Retorna lista vacía si todo OK.
    """
    errors: list[TraceValidationError] = []

    if not record.request_id:
        errors.append(TraceValidationError(field="request_id", reason="no puede ser vacío"))

    if record.tokens_in < 0:
        errors.append(TraceValidationError(field="tokens_in", reason="debe ser >= 0"))

    if record.tokens_out < 0:
        errors.append(TraceValidationError(field="tokens_out", reason="debe ser >= 0"))

    if record.latency_ms < 0:
        errors.append(TraceValidationError(field="latency_ms", reason="debe ser >= 0"))

    if record.retry_count < 0:
        errors.append(TraceValidationError(field="retry_count", reason="debe ser >= 0"))

    if record.top_k_docs < 0:
        errors.append(TraceValidationError(field="top_k_docs", reason="debe ser >= 0"))

    for metric, score in record.eval_scores.items():
        if not (0.0 <= score <= 1.0):
            errors.append(
                TraceValidationError(
                    field=f"eval_scores[{metric!r}]",
                    reason=f"debe estar en [0, 1], valor actual: {score}",
                )
            )

    return errors
