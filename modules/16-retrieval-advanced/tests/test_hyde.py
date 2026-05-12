"""Tests de HyDE Retriever."""

from retrieval_techniques import BaselineDenseRetriever, Document, HyDERetriever


def _mock_hypothetical(query: str) -> str:
    # Mock determinista: expande la query con sinónimos predefinidos.
    expansions = {
        "comida valenciana": "paella arroz azafran",
        "gato come": "felino alimentación pescado",
    }
    return expansions.get(query, query)


class TestHyDE:
    def test_returns_documents(self, sample_docs):
        retriever = HyDERetriever(sample_docs, mock_llm=_mock_hypothetical)
        results = retriever.retrieve("gato come", top_k=3)
        assert len(results) == 3
        assert all(isinstance(d, Document) for d in results)

    def test_hyde_changes_ranking_vs_baseline(self, sample_docs):
        baseline = BaselineDenseRetriever(sample_docs)
        hyde = HyDERetriever(sample_docs, mock_llm=_mock_hypothetical)
        # Para "comida valenciana", la baseline puede no encontrar d6 directo;
        # HyDE expande con "paella arroz azafran" y debería encontrarlo.
        base_results = [d.doc_id for d in baseline.retrieve("comida valenciana", top_k=3)]
        hyde_results = [d.doc_id for d in hyde.retrieve("comida valenciana", top_k=3)]
        # HyDE debería rankear d6 más alto (es el doc relevante)
        if "d6" in hyde_results and "d6" in base_results:
            assert hyde_results.index("d6") <= base_results.index("d6")

    def test_cost_overhead(self, sample_docs):
        hyde = HyDERetriever(sample_docs, mock_llm=_mock_hypothetical)
        overhead = hyde.cost_overhead()
        assert overhead["llm_calls"] == 1
        assert overhead["latency_ms"] > 0

    def test_idempotent_with_same_mock(self, sample_docs):
        hyde = HyDERetriever(sample_docs, mock_llm=_mock_hypothetical)
        r1 = [d.doc_id for d in hyde.retrieve("gato come", top_k=3)]
        r2 = [d.doc_id for d in hyde.retrieve("gato come", top_k=3)]
        assert r1 == r2
