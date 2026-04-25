from __future__ import annotations

import os
import time

import pytest

from src.mock_collector import MockCollector
from src.tracer import trace


class TestTracer:

    def test_decorated_function_creates_span(self, collector: MockCollector) -> None:
        @trace("my_function")
        def fn(x: str) -> str:
            return f"result:{x}"

        fn("hello")
        spans = collector.get_spans()
        print(f"\n  spans: {[s.name for s in spans]}")
        assert len(spans) == 1
        assert spans[0].name == "my_function"

    def test_span_contains_input_output_duration(self, collector: MockCollector) -> None:
        @trace("pipeline_step")
        def process(text: str) -> str:
            return text.upper()

        process("test input")
        span = collector.get_spans("pipeline_step")[0]
        print(f"\n  span: input={span.input!r} output={span.output!r} duration={span.duration_ms}ms")
        assert span.input == "test input"
        assert span.output == "TEST INPUT"
        assert span.duration_ms >= 0.0

    def test_exception_marks_span_error(self, collector: MockCollector) -> None:
        @trace("failing_step")
        def failing(x: str) -> str:
            raise ValueError("something went wrong")

        with pytest.raises(ValueError):
            failing("bad input")

        span = collector.get_spans("failing_step")[0]
        print(f"\n  error span: status={span.status} error={span.error!r}")
        assert span.status == "ERROR"
        assert "something went wrong" in (span.error or "")

    def test_nested_spans_parent_child_relationship(self, collector: MockCollector) -> None:
        @trace("outer")
        def outer_fn(x: str) -> str:
            return inner_fn(x)

        @trace("inner")
        def inner_fn(x: str) -> str:
            return f"processed:{x}"

        outer_fn("data")
        outer_span = collector.get_spans("outer")[0]
        inner_span = collector.get_spans("inner")[0]
        print(f"\n  outer.span_id={outer_span.span_id} inner.parent_id={inner_span.parent_id}")
        assert inner_span.parent_id == outer_span.span_id

    def test_collector_accumulates_multiple_calls(self, collector: MockCollector) -> None:
        @trace("repeated")
        def fn(x: str) -> str:
            return x

        fn("a")
        fn("b")
        fn("c")
        spans = collector.get_spans("repeated")
        assert len(spans) == 3

    def test_get_spans_filters_by_name(self, collector: MockCollector) -> None:
        @trace("alpha")
        def alpha(x: str) -> str:
            return x

        @trace("beta")
        def beta(x: str) -> str:
            return x

        alpha("x")
        beta("y")
        alpha("z")

        alpha_spans = collector.get_spans("alpha")
        beta_spans = collector.get_spans("beta")
        assert len(alpha_spans) == 2
        assert len(beta_spans) == 1

    def test_export_returns_dict_structure(self, collector: MockCollector) -> None:
        @trace("export_test", model="gpt-4")
        def fn(x: str) -> str:
            return x

        fn("value")
        exported = collector.export()
        assert len(exported) == 1
        d = exported[0]
        required_keys = {"name", "attributes", "input", "output", "duration_ms", "status", "error", "parent_id", "span_id"}
        assert set(d.keys()) == required_keys
        assert d["name"] == "export_test"

    @pytest.mark.slow
    def test_real_langfuse_export(self) -> None:
        if not os.getenv("LANGFUSE_SECRET_KEY"):
            pytest.skip("LANGFUSE_SECRET_KEY no encontrado")
        from src import tracer as tm
        from src.mock_collector import MockCollector as MC
        coll = MC()
        tm.set_collector(coll)

        @trace("langfuse_test")
        def fn(x: str) -> str:
            time.sleep(0.01)
            return f"result:{x}"

        fn("input_data")
        spans = coll.get_spans()
        assert len(spans) == 1
        assert spans[0].duration_ms > 0
        tm.set_collector(None)  # type: ignore[arg-type]
        print(f"\n  Span exported locally: {spans[0].name} ({spans[0].duration_ms}ms)")
