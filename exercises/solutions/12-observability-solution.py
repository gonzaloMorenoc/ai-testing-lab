"""
Solución módulo 12: @trace con token_count en attributes.
"""
from __future__ import annotations

import sys
from functools import wraps
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "modules" / "12-observability"))

from src.mock_collector import MockCollector
from src.tracer import set_collector, trace


def trace_with_token_count(name: str, **extra: Any) -> Callable:
    base_decorator = trace(name, **extra)

    def decorator(fn: Callable) -> Callable:
        wrapped = base_decorator(fn)

        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = wrapped(*args, **kwargs)
            from src import tracer as tm
            if tm._collector is not None:
                last_spans = tm._collector.get_spans(name)
                if last_spans:
                    last_spans[-1].attributes["token_count"] = len(str(result).split())
            return result

        return wrapper

    return decorator


if __name__ == "__main__":
    coll = MockCollector()
    set_collector(coll)

    @trace_with_token_count("llm_call")
    def mock_llm(prompt: str) -> str:
        return "The answer is forty-two words long in this example"

    mock_llm("What is 42?")
    span = coll.get_spans("llm_call")[0]
    print(f"token_count in attributes: {span.attributes.get('token_count')}")
    exported = coll.export()
    print(f"exported keys: {list(exported[0].keys())}")
