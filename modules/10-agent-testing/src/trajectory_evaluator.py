from __future__ import annotations

from dataclasses import dataclass
from itertools import zip_longest
from typing import Callable

from src.simple_agent import ToolCall


@dataclass
class ToolCallAccuracyResult:
    score: float
    reason: str

    @property
    def passed(self) -> bool:
        return self.score >= 0.5


@dataclass
class AgentGoalResult:
    achieved: bool
    score: float
    reason: str


class TrajectoryEvaluator:

    def tool_call_accuracy(
        self,
        actual: list[ToolCall],
        expected: list[tuple[str, str]],  # (tool_name, arg_fragment_or_empty)
    ) -> ToolCallAccuracyResult:
        """Score 0-1: exact match=1, right tool wrong arg=0.5/step, wrong tool=0."""
        if not expected:
            return ToolCallAccuracyResult(score=1.0, reason="no expected calls")
        if not actual:
            return ToolCallAccuracyResult(score=0.0, reason="no calls made")

        correct = 0.0
        for act, exp in zip_longest(actual, expected):
            if act is None or exp is None:
                continue
            exp_tool, exp_arg_fragment = exp
            if act.tool == exp_tool:
                if not exp_arg_fragment or exp_arg_fragment.lower() in act.argument.lower():
                    correct += 1.0
                else:
                    correct += 0.5  # right tool, wrong argument

        total = max(len(actual), len(expected))
        score = round(correct / total, 3)

        if score == 1.0 and len(actual) == len(expected):
            reason = "exact match"
        elif len(actual) > len(expected):
            extra = len(actual) - len(expected)
            reason = f"extra steps: {extra} unexpected call(s)"
        elif len(actual) < len(expected):
            missing = len(expected) - len(actual)
            reason = f"missing steps: {missing} call(s) not made"
        else:
            reason = f"partial: score={score:.3f}"

        return ToolCallAccuracyResult(score=score, reason=reason)

    def agent_goal_accuracy(
        self,
        final_output: str,
        goal_checker: Callable[[str], bool],
    ) -> AgentGoalResult:
        achieved = goal_checker(final_output)
        return AgentGoalResult(
            achieved=achieved,
            score=1.0 if achieved else 0.0,
            reason="goal achieved" if achieved else "goal not achieved",
        )
