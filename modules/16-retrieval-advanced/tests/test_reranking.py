"""Tests de CrossEncoderReranker."""

from retrieval_techniques import BaselineDenseRetriever, CrossEncoderReranker


def _mock_scorer(query: str, doc: str) -> float:
    """Mock cross-encoder: bonifica documentos con la palabra exacta."""
    q_words = query.lower().split()
    d_words = doc.lower().split()
    overlap = len(set(q_words) & set(d_words))
    # Bonus si todas las palabras de la query están en el doc
    bonus = 1.0 if all(w in d_words for w in q_words) else 0.0
    return overlap + bonus


class TestReranker:
    def test_returns_top_k(self, sample_docs):
        base = BaselineDenseRetriever(sample_docs)
        reranker = CrossEncoderReranker(base, mock_scorer=_mock_scorer)
        results = reranker.retrieve("gato come", top_k=3)
        assert len(results) == 3

    def test_reorders_candidates(self, sample_docs):
        base = BaselineDenseRetriever(sample_docs)
        reranker = CrossEncoderReranker(base, mock_scorer=_mock_scorer)
        # d1 tiene "gato" y "come"; el scorer debería rankearlo arriba
        results = reranker.retrieve("gato come", top_k=5)
        ids = [d.doc_id for d in results]
        assert ids[0] == "d1"

    def test_cost_overhead(self, sample_docs):
        base = BaselineDenseRetriever(sample_docs)
        reranker = CrossEncoderReranker(base, mock_scorer=_mock_scorer)
        overhead = reranker.cost_overhead()
        assert overhead["model_calls"] == 1
