from __future__ import annotations

import os

import pytest

from src.simple_agent import AgentResult, SimpleAgent, ToolCall
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
