from __future__ import annotations

import re
from dataclasses import dataclass

# Minimum token length for tokenization
_MIN_TOKEN_LENGTH = 3

# Synonym clusters for topic-aware relevance matching in context_precision.
# Words within the same cluster are treated as semantically equivalent.
_DEFAULT_SYNONYM_CLUSTERS: list[frozenset[str]] = [
    frozenset({"return", "refund", "returns", "refunds", "reimburs"}),
    frozenset({"ship", "deliver", "shipping", "delivery", "shipment"}),
    frozenset({"warrant", "warranty", "guarantee", "guaranty"}),
    frozenset({"pay", "payment", "paying", "paid", "credit", "debit"}),
]

# Keep legacy name for backwards compat
_SYNONYM_CLUSTERS = _DEFAULT_SYNONYM_CLUSTERS


def build_synonym_clusters(
    custom_clusters: list[list[str]] | None = None,
    *,
    include_defaults: bool = True,
) -> list[frozenset[str]]:
    """Build a synonym cluster list for a specific domain.

    Args:
        custom_clusters: Domain-specific synonym groups, e.g.
            [["diagnose", "diagnosis", "diagnoses"],
             ["prescribe", "prescription", "prescribed"]]
        include_defaults: Whether to include the built-in e-commerce clusters.

    Returns:
        Combined list of frozensets ready to pass to RAGASEvaluator.

    Example::

        medical_clusters = build_synonym_clusters(
            [["diagnose", "diagnosis"], ["treat", "treatment", "therapy"]],
            include_defaults=False,
        )
        evaluator = RAGASEvaluator(synonym_clusters=medical_clusters)
    """
    clusters: list[frozenset[str]] = list(_DEFAULT_SYNONYM_CLUSTERS) if include_defaults else []
    if custom_clusters:
        clusters.extend(frozenset(group) for group in custom_clusters)
    return clusters


@dataclass
class RAGASScores:
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float

    def passes(self, threshold: float = 0.7) -> bool:
        return all(
            s >= threshold
            for s in [
                self.faithfulness,
                self.answer_relevancy,
                self.context_precision,
                self.context_recall,
            ]
        )

    def __repr__(self) -> str:
        return (
            f"RAGASScores("
            f"faithfulness={self.faithfulness:.2f}, "
            f"answer_relevancy={self.answer_relevancy:.2f}, "
            f"context_precision={self.context_precision:.2f}, "
            f"context_recall={self.context_recall:.2f})"
        )


class RAGASEvaluator:
    def __init__(
        self,
        synonym_clusters: list[frozenset[str]] | None = None,
    ) -> None:
        self._clusters = (
            synonym_clusters if synonym_clusters is not None else _DEFAULT_SYNONYM_CLUSTERS
        )

    def _tokenize(self, text: str) -> set[str]:
        """Return cleaned lowercase tokens with length > 3, punctuation stripped."""
        tokens = set()
        for word in text.split():
            cleaned = re.sub(r"[^a-z0-9]", "", word.lower())
            if len(cleaned) > _MIN_TOKEN_LENGTH:
                tokens.add(cleaned)
        return tokens

    def _expand_synonyms(self, tokens: set[str]) -> set[str]:
        expanded = set(tokens)
        for cluster in self._clusters:
            if tokens & cluster:
                expanded |= cluster
        return expanded

    def faithfulness(self, response: str, context: list[str]) -> float:
        if not context:
            return 0.0
        combined = " ".join(context)
        response_tokens = self._tokenize(response)
        context_tokens = self._tokenize(combined)
        if not response_tokens:
            return 1.0
        supported = response_tokens & context_tokens
        return round(len(supported) / len(response_tokens), 3)

    def answer_relevancy(self, query: str, response: str) -> float:
        query_tokens = self._tokenize(query)
        response_tokens = self._tokenize(response)
        if not query_tokens:
            return 1.0
        overlap = query_tokens & response_tokens
        return round(min(1.0, len(overlap) / len(query_tokens) * 2), 3)

    def context_precision(self, query: str, context: list[str]) -> float:
        if not context:
            return 0.0
        query_tokens = self._tokenize(query)
        expanded_query = self._expand_synonyms(query_tokens)
        relevant = sum(1 for chunk in context if expanded_query & self._tokenize(chunk))
        return round(relevant / len(context), 3)

    def context_recall(self, response: str, context: list[str]) -> float:
        if not context:
            return 0.0
        combined_tokens = self._tokenize(" ".join(context))
        response_tokens = self._tokenize(response)
        if not response_tokens:
            return 1.0
        covered = response_tokens & combined_tokens
        return round(len(covered) / len(response_tokens), 3)

    def evaluate(self, query: str, response: str, context: list[str]) -> RAGASScores:
        return RAGASScores(
            faithfulness=self.faithfulness(response, context),
            answer_relevancy=self.answer_relevancy(query, response),
            context_precision=self.context_precision(query, context),
            context_recall=self.context_recall(response, context),
        )
