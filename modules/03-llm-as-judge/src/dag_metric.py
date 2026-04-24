from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class DAGNode:
    name: str
    condition: Callable[[str], bool]
    score_if_true: float
    score_if_false: float
    reason_true: str
    reason_false: str


@dataclass
class DAGResult:
    score: float
    passed: bool
    reason: str
    node_name: str
    threshold: float

    def __repr__(self) -> str:
        status = "✓" if self.passed else "✗"
        return f"DAG[{status}] node={self.node_name} score={self.score:.2f}"


class DAGMetric:
    def __init__(self, nodes: list[DAGNode], threshold: float = 0.7) -> None:
        self.nodes = nodes
        self.threshold = threshold

    def evaluate(self, output: str) -> DAGResult:
        for node in self.nodes:
            if node.condition(output):
                score = node.score_if_true
                reason = node.reason_true
                node_name = node.name
                break
        else:
            last = self.nodes[-1]
            score = last.score_if_false
            reason = last.reason_false
            node_name = last.name

        return DAGResult(
            score=score,
            passed=score >= self.threshold,
            reason=reason,
            node_name=node_name,
            threshold=self.threshold,
        )


def build_keyword_dag(required_keywords: list[str], threshold: float = 0.7) -> DAGMetric:
    nodes = [
        DAGNode(
            name=f"contains_{kw}",
            condition=lambda output, k=kw: k.lower() in output.lower(),
            score_if_true=1.0,
            score_if_false=0.0,
            reason_true=f"Output contains required keyword '{kw}'",
            reason_false=f"Output missing required keyword '{kw}'",
        )
        for kw in required_keywords
    ]
    return DAGMetric(nodes, threshold)


def build_compound_dag(
    and_keywords: list[str],
    or_keywords: list[str],
    threshold: float = 0.7,
) -> DAGMetric:
    def and_condition(output: str) -> bool:
        return all(kw.lower() in output.lower() for kw in and_keywords)

    def or_condition(output: str) -> bool:
        return any(kw.lower() in output.lower() for kw in or_keywords)

    nodes = [
        DAGNode(
            name="and_check",
            condition=and_condition,
            score_if_true=1.0,
            score_if_false=0.0,
            reason_true=f"All required terms present: {and_keywords}",
            reason_false=f"Missing some required terms: {and_keywords}",
        ),
        DAGNode(
            name="or_fallback",
            condition=or_condition,
            score_if_true=0.6,
            score_if_false=0.0,
            reason_true=f"At least one optional term present: {or_keywords}",
            reason_false="No relevant terms found",
        ),
    ]
    return DAGMetric(nodes, threshold)
