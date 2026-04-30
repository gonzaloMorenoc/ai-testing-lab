from __future__ import annotations

import os

import pytest

from src.simple_agent import SimpleAgent, ToolCall
from src.trajectory_evaluator import TrajectoryEvaluator


class TestSimpleAgent:
    def test_search_query_selects_search_tool(self, agent: SimpleAgent) -> None:
        result = agent.run("What is machine learning?")
        print(f"\n  trajectory: {result.trajectory}")
        assert result.trajectory[0].tool == "search"
        assert "Search result" in result.final_output

    def test_math_query_selects_calculate_tool(self, agent: SimpleAgent) -> None:
        result = agent.run("calculate 2 + 3")
        assert result.trajectory[0].tool == "calculate"
        assert result.final_output == "5"


class TestTrajectoryEvaluator:
    def test_wrong_tool_accuracy_zero(self) -> None:
        evaluator = TrajectoryEvaluator()
        actual = [ToolCall("calculate", "2+3", "5")]
        expected = [("search", "machine learning")]
        result = evaluator.tool_call_accuracy(actual, expected)
        print(f"\n  {result.reason}")
        assert result.score == 0.0

    def test_wrong_arg_correct_tool_partial_credit(self) -> None:
        evaluator = TrajectoryEvaluator()
        actual = [ToolCall("search", "wrong query", "Search result for: wrong query")]
        expected = [("search", "machine learning")]
        result = evaluator.tool_call_accuracy(actual, expected)
        assert result.score == 0.5

    def test_complete_trajectory_exact_match(self) -> None:
        evaluator = TrajectoryEvaluator()
        actual = [
            ToolCall("search", "ai basics", "Search result for: ai basics"),
            ToolCall("calculate", "3 + 4", "7"),
            ToolCall("format_response", "ai summary", "Report:\nai summary"),
        ]
        expected = [("search", "ai basics"), ("calculate", "3 + 4"), ("format_response", "")]
        result = evaluator.tool_call_accuracy(actual, expected)
        print(f"\n  {result.reason}")
        assert result.score == 1.0
        assert result.reason == "exact match"

    def test_extra_step_penalty(self) -> None:
        evaluator = TrajectoryEvaluator()
        actual = [
            ToolCall("search", "query", "result"),
            ToolCall("calculate", "1+1", "2"),
            ToolCall("format_response", "data", "Report:\ndata"),
            ToolCall("search", "extra", "extra result"),
        ]
        expected = [("search", ""), ("calculate", ""), ("format_response", "")]
        result = evaluator.tool_call_accuracy(actual, expected)
        assert result.score < 1.0
        assert "extra" in result.reason

    def test_missing_step_penalty(self) -> None:
        evaluator = TrajectoryEvaluator()
        actual = [
            ToolCall("search", "query", "result"),
            ToolCall("calculate", "1+1", "2"),
        ]
        expected = [("search", ""), ("calculate", ""), ("format_response", "")]
        result = evaluator.tool_call_accuracy(actual, expected)
        assert result.score < 1.0
        assert "missing" in result.reason

    def test_agent_goal_accuracy_achieved(self) -> None:
        evaluator = TrajectoryEvaluator()
        result = evaluator.agent_goal_accuracy(
            final_output="The capital of France is Paris.",
            goal_checker=lambda out: "Paris" in out,
        )
        print(f"\n  goal: {result.reason}")
        assert result.achieved is True
        assert result.score == 1.0

    def test_agent_goal_accuracy_not_achieved(self) -> None:
        evaluator = TrajectoryEvaluator()
        result = evaluator.agent_goal_accuracy(
            final_output="I don't know the answer.",
            goal_checker=lambda out: "Paris" in out,
        )
        assert result.achieved is False
        assert result.score == 0.0

    @pytest.mark.slow
    def test_real_groq_agent(self) -> None:
        if not os.getenv("GROQ_API_KEY"):
            pytest.skip("GROQ_API_KEY no encontrado")
        from groq import Groq  # type: ignore

        client = Groq()

        def groq_search(query: str) -> str:
            resp = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "Answer in one short sentence."},
                    {"role": "user", "content": query},
                ],
                temperature=0.0,
                max_tokens=60,
            )
            return resp.choices[0].message.content or ""

        evaluator = TrajectoryEvaluator()
        output = groq_search("What is 2 + 2?")
        result = evaluator.agent_goal_accuracy(
            final_output=output,
            goal_checker=lambda out: "4" in out,
        )
        print(f"\n  Groq output: {output!r} → achieved={result.achieved}")
        assert isinstance(result.achieved, bool)


# ---------------------------------------------------------------------------
# §18.6  AgentPolicy  +  Cap 27  ToolSchemaValidator
# ---------------------------------------------------------------------------

from src.agent_policy import (  # noqa: E402
    AgentPolicy,
    PolicyViolationError,
    enforce_policy,
    validate_tool_call,
)

EXAMPLE_SCHEMAS: dict = {
    "send_email": {
        "type": "object",
        "required": ["to", "subject", "body"],
        "properties": {
            "to": {"type": "string", "format": "email"},
            "subject": {"type": "string", "maxLength": 200},
            "body": {"type": "string"},
        },
    }
}


class TestEnforcePolicy:
    def _policy(self, **kwargs) -> AgentPolicy:
        defaults = dict(
            allowed_tools={"send_email", "search"},
            max_iterations=5,
            max_cost_usd=1.0,
            human_approval_required={"send_email"},
        )
        defaults.update(kwargs)
        return AgentPolicy(**defaults)

    def test_valid_call_does_not_raise(self) -> None:
        policy = self._policy()
        # send_email is in allowed_tools and human_approval_required → needs approval
        # use "search" which is allowed and NOT in human_approval_required
        enforce_policy("search", {}, policy, iterations_so_far=0, cost_so_far=0.0)

    def test_tool_not_in_allowlist_raises(self) -> None:
        policy = self._policy()
        with pytest.raises(PolicyViolationError, match="allowlist"):
            enforce_policy("delete_file", {}, policy, iterations_so_far=0, cost_so_far=0.0)

    def test_max_iterations_reached_raises(self) -> None:
        policy = self._policy()
        with pytest.raises(PolicyViolationError, match="max_iterations"):
            enforce_policy("search", {}, policy, iterations_so_far=5, cost_so_far=0.0)

    def test_budget_exceeded_raises(self) -> None:
        policy = self._policy()
        with pytest.raises(PolicyViolationError, match="Presupuesto"):
            enforce_policy("search", {}, policy, iterations_so_far=0, cost_so_far=1.5)

    def test_human_approval_required_without_approval_raises(self) -> None:
        policy = self._policy()
        with pytest.raises(PolicyViolationError, match="aprobación humana"):
            enforce_policy(
                "send_email",
                {},
                policy,
                iterations_so_far=0,
                cost_so_far=0.0,
                human_approved=False,
            )

    def test_human_approval_required_with_approval_does_not_raise(self) -> None:
        policy = self._policy()
        enforce_policy(
            "send_email",
            {},
            policy,
            iterations_so_far=0,
            cost_so_far=0.0,
            human_approved=True,
        )


class TestValidateToolCall:
    def test_valid_args_returns_valid_true(self) -> None:
        args = {"to": "user@example.com", "subject": "Hello", "body": "Hi there"}
        result = validate_tool_call("send_email", args, EXAMPLE_SCHEMAS)
        assert result.valid is True
        assert result.error is None

    def test_unregistered_tool_returns_valid_false(self) -> None:
        result = validate_tool_call("unknown_tool", {}, EXAMPLE_SCHEMAS)
        assert result.valid is False
        assert result.error is not None
        assert "no registrada" in result.error

    def test_missing_required_field_returns_valid_false(self) -> None:
        args = {"to": "user@example.com", "subject": "Hello"}  # body missing
        result = validate_tool_call("send_email", args, EXAMPLE_SCHEMAS)
        assert result.valid is False
        assert result.error is not None
        assert "body" in result.error

    def test_invalid_email_format_returns_valid_false(self) -> None:
        args = {"to": "not-an-email", "subject": "Hello", "body": "Hi"}
        result = validate_tool_call("send_email", args, EXAMPLE_SCHEMAS)
        assert result.valid is False
        assert result.error is not None
        assert "email" in result.error.lower()

    def test_valid_email_format_returns_valid_true(self) -> None:
        args = {"to": "valid@domain.org", "subject": "Hello", "body": "Hi"}
        result = validate_tool_call("send_email", args, EXAMPLE_SCHEMAS)
        assert result.valid is True

    def test_max_length_exceeded_returns_valid_false(self) -> None:
        long_subject = "x" * 201
        args = {"to": "user@example.com", "subject": long_subject, "body": "Hi"}
        result = validate_tool_call("send_email", args, EXAMPLE_SCHEMAS)
        assert result.valid is False
        assert result.error is not None
        assert "maxLength" in result.error


# ---------------------------------------------------------------------------
# Cap 18 Tabla 18.X — AgentMetrics (nuevas métricas)
# ---------------------------------------------------------------------------

from src.agent_metrics import (  # noqa: E402
    AgentMetricsReport,
    compute_context_retention_rate,
    compute_hallucination_rate_per_tool,
    compute_human_handoff_rate,
    compute_recovery_rate,
)


class TestAgentMetrics:
    # --- recovery_rate ---

    def test_recovery_rate_all_recovered(self) -> None:
        result = compute_recovery_rate([(True, True), (True, True)])
        assert result.rate == 1.0
        assert result.total_failures == 2
        assert result.recovered == 2

    def test_recovery_rate_none_recovered(self) -> None:
        result = compute_recovery_rate([(True, False), (True, False)])
        assert result.rate == 0.0
        assert result.total_failures == 2
        assert result.recovered == 0

    def test_recovery_rate_no_failures(self) -> None:
        result = compute_recovery_rate([(False, False)])
        assert result.rate == 0.0
        assert result.total_failures == 0

    def test_recovery_rate_partial(self) -> None:
        result = compute_recovery_rate([(True, True), (True, False)])
        assert result.rate == 0.5
        assert result.recovered == 1

    # --- human_handoff_rate ---

    def test_human_handoff_all(self) -> None:
        result = compute_human_handoff_rate([True, True, True])
        assert result.rate == 1.0
        assert result.handoffs == 3

    def test_human_handoff_none(self) -> None:
        result = compute_human_handoff_rate([False, False])
        assert result.rate == 0.0
        assert result.handoffs == 0

    def test_human_handoff_empty(self) -> None:
        result = compute_human_handoff_rate([])
        assert result.rate == 0.0
        assert result.total_tasks == 0

    # --- context_retention_rate ---

    def test_context_retention_all(self) -> None:
        result = compute_context_retention_rate(
            facts=["returns"],
            responses=["returns allowed"],
        )
        assert result.rate == 1.0
        assert result.retained == 1

    def test_context_retention_none(self) -> None:
        result = compute_context_retention_rate(
            facts=["xyz123"],
            responses=["hello world"],
        )
        assert result.rate == 0.0
        assert result.retained == 0

    def test_context_retention_partial(self) -> None:
        result = compute_context_retention_rate(
            facts=["Paris capital", "unknown_word_zzzq"],
            responses=["The city of Paris is beautiful"],
        )
        # "Paris" (5 chars) appears; "unknown_word_zzzq" → "unknown" not in responses
        assert result.total_facts == 2
        assert result.retained == 1
        assert result.rate == 0.5

    # --- hallucination_rate_per_tool ---

    def test_hallucination_rate_no_hallucination(self) -> None:
        calls = [("search", {"query": "hello"}, {"query"})]
        result = compute_hallucination_rate_per_tool(calls)
        assert result.rate == 0.0
        assert result.hallucinated == 0

    def test_hallucination_rate_missing_key(self) -> None:
        calls = [("search", {}, {"query"})]  # required "query" missing
        result = compute_hallucination_rate_per_tool(calls)
        assert result.rate == 1.0
        assert result.hallucinated == 1

    def test_hallucination_rate_extra_key(self) -> None:
        calls = [("search", {"query": "hello", "extra": "invented"}, {"query"})]
        result = compute_hallucination_rate_per_tool(calls)
        assert result.rate == 1.0
        assert result.hallucinated == 1

    # --- AgentMetricsReport ---

    def test_agent_metrics_report_overall_health(self) -> None:
        report = AgentMetricsReport(
            tool_accuracy=0.9,
            goal_achievement_rate=0.8,
            recovery_rate=0.7,
            human_handoff_rate=0.1,
            context_retention_rate=0.85,
            hallucination_rate_per_tool=0.05,
        )
        health = report.overall_health
        assert 0.0 <= health <= 1.0

    def test_agent_metrics_report_frozen(self) -> None:
        report = AgentMetricsReport(
            tool_accuracy=1.0,
            goal_achievement_rate=1.0,
            recovery_rate=1.0,
            human_handoff_rate=0.0,
            context_retention_rate=1.0,
            hallucination_rate_per_tool=0.0,
        )
        with pytest.raises(AttributeError):
            report.tool_accuracy = 0.5  # type: ignore[misc]

    def test_agent_metrics_report_perfect_health(self) -> None:
        report = AgentMetricsReport(
            tool_accuracy=1.0,
            goal_achievement_rate=1.0,
            recovery_rate=1.0,
            human_handoff_rate=0.0,
            context_retention_rate=1.0,
            hallucination_rate_per_tool=0.0,
        )
        assert report.overall_health == 1.0
