"""Smoke test del golden dataset y corpus del módulo 16."""

import json
from pathlib import Path

import pytest

GOLDEN_DIR = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "goldens"
    / "16-retrieval-advanced"
)


def _load_queries() -> list[dict]:
    with (GOLDEN_DIR / "queries.jsonl").open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _load_corpus() -> dict:
    return json.loads((GOLDEN_DIR / "corpus.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def queries() -> list[dict]:
    return _load_queries()


@pytest.fixture(scope="module")
def corpus() -> dict:
    return _load_corpus()


class TestGoldenQueries:
    def test_at_least_100_queries(self, queries):
        """Manual §9.2: mínimo 100 entradas."""
        assert len(queries) >= 100

    def test_8_query_shapes_present(self, queries):
        shapes = {q["query_shape"] for q in queries}
        assert len(shapes) == 8

    def test_stratification_at_least_10_per_shape(self, queries):
        from collections import Counter

        counts = Counter(q["query_shape"] for q in queries)
        # Cobertura mínima para reportar consistency_mean por segmento
        for shape, n in counts.items():
            assert n >= 10, f"{shape} solo tiene {n} queries"

    def test_qrels_reference_corpus_docs(self, queries, corpus):
        for q in queries:
            for doc_id in q["qrels"]:
                assert doc_id in corpus, f"qrel doc_id {doc_id} no está en corpus"

    def test_qrels_grades_in_valid_range(self, queries):
        for q in queries:
            for grade in q["qrels"].values():
                assert 0 <= grade <= 3


class TestCorpus:
    def test_at_least_20_docs(self, corpus):
        assert len(corpus) >= 20

    def test_all_docs_have_text_and_domain(self, corpus):
        for doc_id, doc in corpus.items():
            assert "text" in doc and "domain" in doc
            assert len(doc["text"]) > 10
