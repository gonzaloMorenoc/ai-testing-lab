"""Tests de trade_offs.py y la función recommend_technique."""

import pytest

from trade_offs import (
    TECHNIQUE_TRADE_OFFS,
    QueryShape,
    recommend_technique,
)


class TestTechniqueTradeOffs:
    def test_all_canonical_techniques_present(self):
        expected = {
            "hyde",
            "query_rewriting",
            "multi_query_n3",
            "hybrid_search",
            "reranking",
            "parent_child",
            "sentence_window",
            "self_rag",
        }
        assert set(TECHNIQUE_TRADE_OFFS.keys()) == expected

    def test_reranking_has_extra_model_call(self):
        assert TECHNIQUE_TRADE_OFFS["reranking"].extra_model_calls == 1

    def test_hybrid_search_has_extra_index(self):
        assert TECHNIQUE_TRADE_OFFS["hybrid_search"].extra_index == "BM25"

    def test_recall_ranges_are_positive(self):
        for _name, t in TECHNIQUE_TRADE_OFFS.items():
            lo, hi = t.recall_improvement_pct
            assert 0 < lo <= hi


class TestRecommendTechnique:
    @pytest.mark.parametrize(
        "shape,expected",
        [
            (QueryShape.SHORT_AMBIGUOUS, "hyde"),
            (QueryShape.CONVERSATIONAL, "query_rewriting"),
            (QueryShape.MULTI_ASPECT, "multi_query_n3"),
            (QueryShape.DOMAIN_JARGON, "hybrid_search"),
            (QueryShape.POSITION_CRITICAL, "reranking"),
            (QueryShape.LARGE_STRUCTURED_DOC, "parent_child"),
            (QueryShape.LOCAL_CONTEXT, "sentence_window"),
            (QueryShape.ITERATIVE_REASONING, "self_rag"),
        ],
    )
    def test_recommendation_per_shape(self, shape, expected):
        assert recommend_technique(shape) == expected

    def test_all_shapes_have_recommendation(self):
        for shape in QueryShape:
            assert recommend_technique(shape) in TECHNIQUE_TRADE_OFFS
