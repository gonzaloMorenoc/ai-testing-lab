from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.tracer import Span


@dataclass
class MockCollector:
    _spans: list[Span] = field(default_factory=list)

    def _add(self, span: Span) -> None:
        self._spans.append(span)

    def get_spans(self, name: str | None = None) -> list[Span]:
        if name is None:
            return list(self._spans)
        return [s for s in self._spans if s.name == name]

    def clear(self) -> None:
        self._spans.clear()

    def export(self) -> list[dict[str, Any]]:
        return [
            {
                "name": s.name,
                "attributes": dict(s.attributes),
                "input": s.input,
                "output": s.output,
                "duration_ms": s.duration_ms,
                "status": s.status,
                "error": s.error,
                "parent_id": s.parent_id,
                "span_id": s.span_id,
            }
            for s in self._spans
        ]
