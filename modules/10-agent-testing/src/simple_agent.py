from __future__ import annotations

import re
from dataclasses import dataclass, field

_CALC_KEYWORDS: tuple[str, ...] = (
    "calculate",
    "compute",
    "how much",
    "how many",
    "sum of",
    "add",
    "multiply",
)
_FORMAT_KEYWORDS: tuple[str, ...] = ("format", "report", "summarize", "structure")
_SAFE_EXPR_RE = re.compile(r"[^0-9\+\-\*/\.\s\(\)]+")


@dataclass(frozen=True)
class ToolCall:
    tool: str
    argument: str
    result: str


@dataclass
class AgentResult:
    query: str
    trajectory: list[ToolCall] = field(default_factory=list)
    final_output: str = ""


class SimpleAgent:

    def search(self, query: str) -> str:
        return f"Search result for: {query}"

    def calculate(self, expr: str) -> str:
        safe = _SAFE_EXPR_RE.sub("", expr).strip()
        if not safe:
            return "0"
        try:
            result = eval(safe, {"__builtins__": {}}, {})  # noqa: S307
            return str(result)
        except Exception:
            return "0"

    def format_response(self, data: str) -> str:
        return f"Report:\n{data}"

    def _select_tool(self, query: str) -> tuple[str, str]:
        low = query.lower()
        if any(k in low for k in _CALC_KEYWORDS):
            match = re.search(r"[\d\s\+\-\*\/\.\(\)]+", query)
            arg = match.group(0).strip() if match else query
            return "calculate", arg
        if any(k in low for k in _FORMAT_KEYWORDS):
            return "format_response", query
        return "search", query

    def run(self, query: str) -> AgentResult:
        result = AgentResult(query=query)
        tool_name, arg = self._select_tool(query)
        tool_fn = getattr(self, tool_name)
        output = tool_fn(arg)
        result.trajectory.append(ToolCall(tool=tool_name, argument=arg, result=output))
        result.final_output = output
        return result
