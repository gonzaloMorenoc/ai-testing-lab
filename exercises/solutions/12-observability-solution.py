"""
Solución módulo 12: @trace con token_count en attributes.
"""
from __future__ import annotations

import sys
import time
import uuid
from functools import wraps
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "modules" / "12-observability"))

from src.mock_collector import MockCollector
from src.tracer import Span, set_collector, _CURRENT_SPAN_ID


def trace_with_token_count(name: str, collector: MockCollector, **extra: Any) -> Callable:
    """Decorator like @trace but adds token_count to attributes."""
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            span = Span(
                name=name,
                attributes={**extra},
                input=str(args[0]) if args else "",
                parent_id=_CURRENT_SPAN_ID.get(),
            )
            token = _CURRENT_SPAN_ID.set(span.span_id)
            start = time.monotonic()
            try:
                result = fn(*args, **kwargs)
                span.output = str(result)
                span.status = "OK"
                span.attributes["token_count"] = len(str(result).split())
                return result
            except Exception as exc:
                span.status = "ERROR"
                span.error = str(exc)
                raise
            finally:
                span.duration_ms = round((time.monotonic() - start) * 1000, 2)
                _CURRENT_SPAN_ID.reset(token)
                collector._add(span)
        return wrapper
    return decorator


if __name__ == "__main__":
    coll = MockCollector()
    set_collector(coll)

    @trace_with_token_count("llm_call", collector=coll)
    def mock_llm(prompt: str) -> str:
        return "The answer is forty-two words long in this example"

    mock_llm("What is 42?")
    span = coll.get_spans("llm_call")[0]
    print(f"token_count in attributes: {span.attributes.get('token_count')}")
    exported = coll.export()
    print(f"exported keys: {list(exported[0].keys())}")
