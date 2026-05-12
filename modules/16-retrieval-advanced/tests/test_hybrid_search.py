"""Tests de HybridSearcher (BM25 + denso con RRF)."""

from retrieval_techniques import HybridSearcher, reciprocal_rank_fusion


class TestReciprocalRankFusion:
    def test_empty_lists(self):
        assert reciprocal_rank_fusion([]) == []

    def test_single_list_preserves_order(self):
        ranking = [("a", 1.0), ("b", 0.5), ("c", 0.1)]
        fused = reciprocal_rank_fusion([ranking])
        assert [doc_id for doc_id, _ in fused] == ["a", "b", "c"]

    def test_combines_two_lists(self):
        l1 = [("a", 0.9), ("b", 0.5)]
        l2 = [("b", 0.8), ("a", 0.4)]
        fused = reciprocal_rank_fusion([l1, l2])
        # a y b deberían quedar arriba; el orden depende de los ranks
        ids = [doc_id for doc_id, _ in fused]
        assert set(ids[:2]) == {"a", "b"}


class TestHybridSearcher:
    def test_retrieves_documents(self, sample_docs):
        searcher = HybridSearcher(sample_docs)
        results = searcher.retrieve("gato", top_k=3)
        assert len(results) == 3

    def test_finds_keyword_matches(self, sample_docs):
        searcher = HybridSearcher(sample_docs)
        # "paella" es muy específico, BM25 debería empujar d6 al top
        results = searcher.retrieve("paella", top_k=3)
        ids = [d.doc_id for d in results]
        assert "d6" in ids

    def test_cost_overhead(self, sample_docs):
        searcher = HybridSearcher(sample_docs)
        overhead = searcher.cost_overhead()
        assert overhead["llm_calls"] == 0
        assert overhead["latency_ms"] > 0
