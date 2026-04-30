"""
Solución módulo 10: agente con tool translate + evaluación de trayectoria.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "modules" / "10-agent-testing"))

from src.simple_agent import SimpleAgent, ToolCall
from src.trajectory_evaluator import TrajectoryEvaluator

_TRANSLATE_KEYWORDS: tuple[str, ...] = ("translate", "in french", "in spanish", "en español")


class ExtendedAgent(SimpleAgent):
    def translate(self, text: str) -> str:
        return f"[translated] {text}"

    def _select_tool(self, query: str) -> tuple[str, str]:
        low = query.lower()
        if any(k in low for k in _TRANSLATE_KEYWORDS):
            return "translate", query
        return super()._select_tool(query)


if __name__ == "__main__":
    agent = ExtendedAgent()
    evaluator = TrajectoryEvaluator()

    result = agent.run("translate hello world in french")
    print(f"Tool: {result.trajectory[0].tool}")
    print(f"Output: {result.final_output}")

    traj = [
        ToolCall("search", "ai news", "Search result for: ai news"),
        ToolCall("calculate", "10 + 5", "15"),
        ToolCall("translate", "hello", "[translated] hello"),
        ToolCall("format_response", "summary", "Report:\nsummary"),
    ]
    expected = [("search", ""), ("calculate", ""), ("translate", ""), ("format_response", "")]
    accuracy = evaluator.tool_call_accuracy(traj, expected)
    print(f"Accuracy: {accuracy.score} — {accuracy.reason}")
