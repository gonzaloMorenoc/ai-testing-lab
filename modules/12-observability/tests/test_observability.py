from __future__ import annotations

import os
import time

import pytest

from src.mock_collector import MockCollector
from src.trace_record import TraceRecord, TraceValidationError, make_trace_record, validate_trace
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


class TestTraceRecord:

    def test_make_trace_record_defaults(self) -> None:
        record = make_trace_record(response="hello", tokens_in=10, tokens_out=5, latency_ms=120.0)
        assert isinstance(record, TraceRecord)
        assert record.response == "hello"
        assert record.tokens_in == 10
        assert record.tokens_out == 5
        assert record.latency_ms == 120.0
        assert record.user_segment == "default"
        assert record.model_id == "unknown"

    def test_make_trace_record_auto_request_id(self) -> None:
        record1 = make_trace_record(response="a", tokens_in=1, tokens_out=1, latency_ms=10.0)
        record2 = make_trace_record(response="b", tokens_in=1, tokens_out=1, latency_ms=10.0)
        assert record1.request_id != ""
        assert record2.request_id != ""
        assert record1.request_id != record2.request_id

    def test_make_trace_record_custom_fields(self) -> None:
        record = make_trace_record(
            response="answer",
            tokens_in=50,
            tokens_out=20,
            latency_ms=300.5,
            request_id="abc123",
            user_segment="premium",
            model_id="claude-sonnet-4-6",
            model_version="20251201",
            prompt_id="p001",
            prompt_version="v2.1",
            retriever_id="faiss-cosine",
            retriever_version="1.0.0",
            top_k_docs=3,
            reranker_scores=(0.9, 0.8, 0.7),
            safety_flags=("toxic_content",),
            pii_flags=("email",),
            tool_calls=("search",),
            error_code=None,
            retry_count=1,
            eval_scores={"faithfulness": 0.87},
        )
        assert record.request_id == "abc123"
        assert record.user_segment == "premium"
        assert record.model_id == "claude-sonnet-4-6"
        assert record.model_version == "20251201"
        assert record.prompt_id == "p001"
        assert record.prompt_version == "v2.1"
        assert record.retriever_id == "faiss-cosine"
        assert record.retriever_version == "1.0.0"
        assert record.top_k_docs == 3
        assert record.reranker_scores == (0.9, 0.8, 0.7)
        assert record.retry_count == 1
        assert record.eval_scores == {"faithfulness": 0.87}

    def test_trace_record_frozen(self) -> None:
        record = make_trace_record(response="x", tokens_in=1, tokens_out=1, latency_ms=1.0)
        with pytest.raises(AttributeError):
            record.response = "mutated"  # type: ignore[misc]

    def test_validate_trace_valid(self) -> None:
        record = make_trace_record(
            response="ok",
            tokens_in=10,
            tokens_out=5,
            latency_ms=50.0,
            eval_scores={"relevancy": 0.95},
        )
        errors = validate_trace(record)
        assert errors == []

    def test_validate_trace_empty_request_id(self) -> None:
        record = make_trace_record(
            response="ok",
            tokens_in=10,
            tokens_out=5,
            latency_ms=50.0,
            request_id="",
        )
        errors = validate_trace(record)
        assert any(e.field == "request_id" for e in errors)

    def test_validate_trace_negative_tokens(self) -> None:
        record = make_trace_record(response="ok", tokens_in=-1, tokens_out=5, latency_ms=50.0)
        errors = validate_trace(record)
        assert any(e.field == "tokens_in" for e in errors)

    def test_validate_trace_negative_latency(self) -> None:
        record = make_trace_record(response="ok", tokens_in=10, tokens_out=5, latency_ms=-1.0)
        errors = validate_trace(record)
        assert any(e.field == "latency_ms" for e in errors)

    def test_validate_trace_invalid_eval_score(self) -> None:
        record = make_trace_record(
            response="ok",
            tokens_in=10,
            tokens_out=5,
            latency_ms=50.0,
            eval_scores={"x": 1.5},
        )
        errors = validate_trace(record)
        assert any("eval_scores" in e.field for e in errors)

    def test_trace_record_safety_flags(self) -> None:
        record = make_trace_record(
            response="flagged",
            tokens_in=10,
            tokens_out=5,
            latency_ms=50.0,
            safety_flags=("toxic",),
        )
        assert record.safety_flags == ("toxic",)

    def test_trace_record_pii_flags(self) -> None:
        record = make_trace_record(
            response="contains pii",
            tokens_in=20,
            tokens_out=10,
            latency_ms=80.0,
            pii_flags=("email", "phone"),
        )
        assert record.pii_flags == ("email", "phone")
        assert len(record.pii_flags) == 2

    def test_trace_record_eval_scores(self) -> None:
        scores = {"faithfulness": 0.87, "relevancy": 0.91}
        record = make_trace_record(
            response="answer",
            tokens_in=30,
            tokens_out=15,
            latency_ms=200.0,
            eval_scores=scores,
        )
        assert record.eval_scores["faithfulness"] == pytest.approx(0.87)
        assert record.eval_scores["relevancy"] == pytest.approx(0.91)

    def test_trace_record_no_retriever(self) -> None:
        record = make_trace_record(
            response="direct answer",
            tokens_in=10,
            tokens_out=5,
            latency_ms=30.0,
            top_k_docs=0,
            reranker_scores=(),
        )
        assert record.top_k_docs == 0
        assert record.reranker_scores == ()
        errors = validate_trace(record)
        assert errors == []

    def test_trace_record_tool_calls(self) -> None:
        record = make_trace_record(
            response="searched and calculated",
            tokens_in=40,
            tokens_out=20,
            latency_ms=150.0,
            tool_calls=("search", "calculator"),
        )
        assert record.tool_calls == ("search", "calculator")
        assert "search" in record.tool_calls
        assert "calculator" in record.tool_calls
