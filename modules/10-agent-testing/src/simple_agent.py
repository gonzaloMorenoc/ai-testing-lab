from __future__ import annotations

import ast
import operator
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

_AST_OPS: dict = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _eval_ast_node(node: ast.expr) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in _AST_OPS:
        return _AST_OPS[type(node.op)](_eval_ast_node(node.left), _eval_ast_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _AST_OPS:
        return _AST_OPS[type(node.op)](_eval_ast_node(node.operand))
    raise ValueError(f"Unsupported expression node: {ast.dump(node)}")


def _safe_eval(expr: str) -> float:
    """Evaluate a numeric expression via AST — no eval(), no builtins access."""
    try:
        tree = ast.parse(expr.strip(), mode="eval")
        return _eval_ast_node(tree.body)
    except Exception:
        return 0.0


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
        result = _safe_eval(safe)
        return str(int(result)) if result == int(result) else str(result)

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
