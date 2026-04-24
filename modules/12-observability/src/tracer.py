from __future__ import annotations

import time
import uuid
from contextvars import ContextVar
from dataclasses import dataclass, field
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from src.mock_collector import MockCollector

_CURRENT_SPAN_ID: ContextVar[str | None] = ContextVar("_current_span_id", default=None)
_collector: "MockCollector | None" = None


def set_collector(collector: "MockCollector | None") -> None:
    global _collector
    _collector = collector


@dataclass
class Span:
    name: str
    attributes: dict[str, Any] = field(default_factory=dict)
    input: str = ""
    output: str = ""
    duration_ms: float = 0.0
    status: str = "OK"
    error: str | None = None
    parent_id: str | None = None
    span_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])


def trace(name: str, **extra_attributes: Any) -> Callable:
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            span = Span(
                name=name,
                attributes=dict(extra_attributes),
                input=str(args[0]) if args else "",
                parent_id=_CURRENT_SPAN_ID.get(),
            )
            token = _CURRENT_SPAN_ID.set(span.span_id)
            start = time.monotonic()
            try:
                result = fn(*args, **kwargs)
                span.output = str(result)
                span.status = "OK"
                return result
            except Exception as exc:
                span.status = "ERROR"
                span.error = str(exc)
                raise
            finally:
                span.duration_ms = round((time.monotonic() - start) * 1000, 2)
                _CURRENT_SPAN_ID.reset(token)
                if _collector is not None:
                    _collector._add(span)

        return wrapper

    return decorator
