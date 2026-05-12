"""Tests de SelfRAGRetriever."""

from retrieval_techniques import BaselineDenseRetriever, SelfRAGRetriever


class TestSelfRAG:
    def test_does_not_retrieve_when_should_retrieve_false(self, sample_docs):
        base = BaselineDenseRetriever(sample_docs)
        retriever = SelfRAGRetriever(base=base, should_retrieve=lambda _q: False)
        assert retriever.retrieve("gato", top_k=3) == []

    def test_retrieves_when_should_retrieve_true(self, sample_docs):
        base = BaselineDenseRetriever(sample_docs)
        retriever = SelfRAGRetriever(base=base, should_retrieve=lambda _q: True)
        results = retriever.retrieve("gato come", top_k=3)
        assert len(results) > 0

    def test_filters_irrelevant_documents(self, sample_docs):
        base = BaselineDenseRetriever(sample_docs)
        # Solo considera relevantes los docs con "gato" en el texto
        retriever = SelfRAGRetriever(
            base=base,
            should_retrieve=lambda _q: True,
            is_relevant=lambda _q, d: "gato" in d.text.lower(),
        )
        results = retriever.retrieve("gato come", top_k=5)
        for d in results:
            assert "gato" in d.text.lower()

    def test_cost_overhead(self, sample_docs):
        base = BaselineDenseRetriever(sample_docs)
        retriever = SelfRAGRetriever(base=base, should_retrieve=lambda _q: True)
        overhead = retriever.cost_overhead()
        # 2 LLM calls: decisión + reflexión
        assert overhead["llm_calls"] == 2
