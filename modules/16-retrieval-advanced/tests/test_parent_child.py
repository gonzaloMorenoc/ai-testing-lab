"""Tests de ParentChildChunker."""

from retrieval_techniques import Document, ParentChildChunker, ParentChildIndex


def _build_index() -> ParentChildIndex:
    parent_a = Document("pA", "Capítulo completo: el gato come pescado y duerme en el sofá.")
    parent_b = Document("pB", "Capítulo completo: Python es versátil para data science y web.")
    children = [
        Document("cA1", "El gato come pescado", parent_id="pA"),
        Document("cA2", "Duerme en el sofá", parent_id="pA"),
        Document("cB1", "Python para data science", parent_id="pB"),
        Document("cB2", "Python para web", parent_id="pB"),
    ]
    parents = {"pA": parent_a, "pB": parent_b}
    return ParentChildIndex(children=children, parents=parents)


class TestParentChildChunker:
    def test_returns_parent_for_matched_child(self):
        chunker = ParentChildChunker(_build_index())
        results = chunker.retrieve("gato come", top_k=2)
        ids = [d.doc_id for d in results]
        assert "pA" in ids

    def test_dedupes_parents(self):
        chunker = ParentChildChunker(_build_index())
        # Si dos children del mismo parent matchean, devolver el parent una vez
        results = chunker.retrieve("python", top_k=5)
        ids = [d.doc_id for d in results]
        assert ids.count("pB") <= 1

    def test_cost_overhead(self):
        chunker = ParentChildChunker(_build_index())
        overhead = chunker.cost_overhead()
        assert overhead["llm_calls"] == 0
