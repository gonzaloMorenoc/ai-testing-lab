"""Tests de la implementación BM25 mínima."""

import pytest

from bm25 import BM25Index, _tokenize


class TestTokenize:
    def test_lowercase(self):
        assert _tokenize("Hola Mundo") == ["hola", "mundo"]

    def test_strips_punctuation(self):
        assert _tokenize("Hola, mundo!") == ["hola", "mundo"]

    def test_preserves_digits(self):
        assert _tokenize("Python 3.11") == ["python", "3", "11"]


class TestBM25Index:
    def test_empty_index_returns_empty(self):
        idx = BM25Index()
        assert idx.search("query", top_k=5) == []

    def test_single_doc_match(self):
        idx = BM25Index()
        idx.add("d1", "el gato negro")
        results = idx.search("gato", top_k=5)
        assert results[0][0] == "d1"
        assert results[0][1] > 0

    def test_ranking_by_term_frequency(self):
        idx = BM25Index()
        idx.add("d1", "gato gato gato gato")  # tf alto
        idx.add("d2", "gato perro pez")  # tf bajo
        results = idx.search("gato", top_k=5)
        assert results[0][0] == "d1"

    def test_idf_penalizes_common_terms(self):
        idx = BM25Index()
        idx.add("d1", "el gato negro")
        idx.add("d2", "el perro blanco")
        idx.add("d3", "el pez rojo")
        # "gato" es raro; "el" es común. La query "gato el" debe priorizar gato.
        results = idx.search("gato el", top_k=3)
        assert results[0][0] == "d1"

    def test_top_k_limits_results(self):
        idx = BM25Index()
        for i in range(20):
            idx.add(f"d{i}", f"gato documento {i}")
        results = idx.search("gato", top_k=5)
        assert len(results) == 5
