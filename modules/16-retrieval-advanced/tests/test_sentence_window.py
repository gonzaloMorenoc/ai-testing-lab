"""Tests de SentenceWindowRetriever."""

from retrieval_techniques import SentenceWindowRetriever


class TestSentenceWindow:
    def test_returns_window_context(self):
        sentences = [
            "Introducción al documento.",
            "El gato come pescado.",
            "Esto sucede cada mañana.",
            "Otro detalle del relato.",
            "Cierre y conclusiones.",
        ]
        retriever = SentenceWindowRetriever(sentences, window=1)
        results = retriever.retrieve("gato come", top_k=1)
        assert len(results) == 1
        # Debería contener la oración 1 (índice 1: "El gato come pescado") + vecinos
        assert "gato" in results[0].text
        # Con window=1 incluye 0 y 2 también
        assert "Introducción" in results[0].text or "mañana" in results[0].text

    def test_window_size(self):
        sentences = ["uno", "dos", "tres gato", "cuatro", "cinco"]
        retriever = SentenceWindowRetriever(sentences, window=2)
        results = retriever.retrieve("gato", top_k=1)
        # Con window=2 e índice 2, debería traer 0,1,2,3,4 ⇒ todos
        words = results[0].text.split()
        assert "uno" in words and "cinco" in words

    def test_top_k_zero_returns_empty(self):
        retriever = SentenceWindowRetriever(["a", "b"], window=1)
        results = retriever.retrieve("nada", top_k=0)
        assert results == []

    def test_cost_overhead(self):
        retriever = SentenceWindowRetriever(["a", "b"], window=1)
        assert retriever.cost_overhead()["llm_calls"] == 0
