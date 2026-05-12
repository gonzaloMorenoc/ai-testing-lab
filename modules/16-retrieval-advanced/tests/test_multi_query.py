"""Tests de MultiQueryRetriever."""

from retrieval_techniques import MultiQueryRetriever


def _mock_variations(query: str) -> list[str]:
    if query == "gato":
        return ["felino domestico", "gato come", "gato duerme"]
    return [query]


class TestMultiQuery:
    def test_returns_deduplicated_results(self, sample_docs):
        retriever = MultiQueryRetriever(sample_docs, mock_llm=_mock_variations, n_variations=3)
        results = retriever.retrieve("gato", top_k=5)
        ids = [d.doc_id for d in results]
        assert len(ids) == len(set(ids))

    def test_uses_n_variations(self, sample_docs):
        retriever = MultiQueryRetriever(sample_docs, mock_llm=_mock_variations, n_variations=2)
        # Si las variaciones devuelven docs distintos, el resultado los une
        results = retriever.retrieve("gato", top_k=10)
        # Al menos debería traer documentos relacionados con gato
        gato_docs = {"d1", "d4", "d8"}
        retrieved_gato = sum(1 for d in results if d.doc_id in gato_docs)
        assert retrieved_gato >= 1

    def test_fallback_when_no_variations(self, sample_docs):
        retriever = MultiQueryRetriever(sample_docs, mock_llm=lambda _q: [], n_variations=3)
        results = retriever.retrieve("gato", top_k=3)
        assert len(results) > 0

    def test_cost_overhead(self, sample_docs):
        retriever = MultiQueryRetriever(sample_docs, mock_llm=_mock_variations, n_variations=3)
        overhead = retriever.cost_overhead()
        assert overhead["extra_retrievals"] == 3
