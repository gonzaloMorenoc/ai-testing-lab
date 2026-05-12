"""Tests de QueryRewriter."""

from retrieval_techniques import QueryRewriter


def _mock_rewrite(query: str) -> str:
    # Reescribe queries conversacionales en forma canónica
    if query.lower().startswith("oye, "):
        return query[5:]
    if "y respecto a" in query.lower():
        return query.lower().split("y respecto a")[-1].strip()
    return query


class TestQueryRewriter:
    def test_strips_conversational_prefix(self, sample_docs):
        rewriter = QueryRewriter(sample_docs, mock_llm=_mock_rewrite)
        original = [d.doc_id for d in rewriter.retrieve("oye, gato come", top_k=3)]
        canonical = [d.doc_id for d in rewriter.retrieve("gato come", top_k=3)]
        assert original == canonical

    def test_cost_overhead(self, sample_docs):
        rewriter = QueryRewriter(sample_docs, mock_llm=_mock_rewrite)
        overhead = rewriter.cost_overhead()
        assert overhead["llm_calls"] == 1
