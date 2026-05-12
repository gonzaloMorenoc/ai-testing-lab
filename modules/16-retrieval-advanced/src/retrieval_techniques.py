"""Capítulo 29 del Manual v13 — Retrieval avanzado.

Implementa las técnicas de la Tabla 29.1 con mocks deterministas (sin LLMs
reales). Cada técnica expone `retrieve(query, top_k)` y `cost_overhead()`.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from bm25 import BM25Index


@dataclass(frozen=True)
class Document:
    doc_id: str
    text: str
    parent_id: str | None = None


def _dense_score(query: str, doc: str) -> float:
    """Mock determinista de embedding similarity por overlap léxico."""
    q = set(query.lower().split())
    d = set(doc.lower().split())
    if not q or not d:
        return 0.0
    return len(q & d) / len(q | d)


class BaselineDenseRetriever:
    """Retriever k-NN sobre embeddings densos (mock)."""

    def __init__(self, docs: list[Document]) -> None:
        self.docs = docs

    def retrieve(self, query: str, top_k: int = 5) -> list[Document]:
        scored = sorted(
            self.docs, key=lambda d: _dense_score(query, d.text), reverse=True
        )
        return scored[:top_k]

    def cost_overhead(self) -> dict[str, float]:
        return {"llm_calls": 0, "model_calls": 0, "latency_ms": 0.0}


class HyDERetriever:
    """Hypothetical Document Embeddings (Gao et al. 2022).

    Genera una respuesta hipotética con un mock_llm y busca por su embedding.
    """

    def __init__(self, docs: list[Document], mock_llm: Callable[[str], str]) -> None:
        self.baseline = BaselineDenseRetriever(docs)
        self.mock_llm = mock_llm

    def retrieve(self, query: str, top_k: int = 5) -> list[Document]:
        hypothetical = self.mock_llm(query)
        # Usa la respuesta hipotética como query expandida
        expanded = f"{query} {hypothetical}"
        return self.baseline.retrieve(expanded, top_k)

    def cost_overhead(self) -> dict[str, float]:
        return {"llm_calls": 1, "model_calls": 0, "latency_ms": 350.0}


class QueryRewriter:
    """Reforma queries conversacionales. Mock con reglas básicas."""

    def __init__(self, docs: list[Document], mock_llm: Callable[[str], str]) -> None:
        self.baseline = BaselineDenseRetriever(docs)
        self.mock_llm = mock_llm

    def retrieve(self, query: str, top_k: int = 5) -> list[Document]:
        rewritten = self.mock_llm(query)
        return self.baseline.retrieve(rewritten, top_k)

    def cost_overhead(self) -> dict[str, float]:
        return {"llm_calls": 1, "model_calls": 0, "latency_ms": 225.0}


class MultiQueryRetriever:
    """Genera N variaciones de la query y une los resultados."""

    def __init__(
        self,
        docs: list[Document],
        mock_llm: Callable[[str], list[str]],
        n_variations: int = 3,
    ) -> None:
        self.baseline = BaselineDenseRetriever(docs)
        self.mock_llm = mock_llm
        self.n_variations = n_variations

    def retrieve(self, query: str, top_k: int = 5) -> list[Document]:
        variations = self.mock_llm(query)[: self.n_variations]
        if not variations:
            variations = [query]
        seen: dict[str, Document] = {}
        for v in variations:
            for d in self.baseline.retrieve(v, top_k):
                if d.doc_id not in seen:
                    seen[d.doc_id] = d
        return list(seen.values())[:top_k]

    def cost_overhead(self) -> dict[str, float]:
        return {
            "llm_calls": 0,
            "model_calls": 0,
            "latency_ms": 150.0,
            "extra_retrievals": float(self.n_variations),
        }


def reciprocal_rank_fusion(
    ranklists: list[list[tuple[str, float]]], k: int = 60
) -> list[tuple[str, float]]:
    """RRF: fusiona varios rankings sumando 1 / (k + rank)."""
    fused: dict[str, float] = {}
    for ranking in ranklists:
        for rank, (doc_id, _score) in enumerate(ranking):
            fused[doc_id] = fused.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
    return sorted(fused.items(), key=lambda x: x[1], reverse=True)


class HybridSearcher:
    """Combina BM25 (keyword) con denso (semántico), fusión RRF."""

    def __init__(self, docs: list[Document]) -> None:
        self.docs = docs
        self._by_id = {d.doc_id: d for d in docs}
        self._bm25 = BM25Index()
        for d in docs:
            self._bm25.add(d.doc_id, d.text)

    def retrieve(self, query: str, top_k: int = 5) -> list[Document]:
        bm25_results = self._bm25.search(query, top_k=top_k * 2)
        dense_results = sorted(
            ((d.doc_id, _dense_score(query, d.text)) for d in self.docs),
            key=lambda x: x[1],
            reverse=True,
        )[: top_k * 2]
        fused = reciprocal_rank_fusion([bm25_results, dense_results])
        return [self._by_id[doc_id] for doc_id, _ in fused[:top_k]]

    def cost_overhead(self) -> dict[str, float]:
        return {"llm_calls": 0, "model_calls": 0, "latency_ms": 75.0, "extra_index": 1.0}


class CrossEncoderReranker:
    """Reordena top-k inicial con un mock_scorer (cross-encoder)."""

    def __init__(
        self,
        base_retriever: BaselineDenseRetriever,
        mock_scorer: Callable[[str, str], float],
    ) -> None:
        self.base = base_retriever
        self.mock_scorer = mock_scorer

    def retrieve(self, query: str, top_k: int = 5) -> list[Document]:
        # Retrieve más de top_k y reordena
        candidates = self.base.retrieve(query, top_k=top_k * 2)
        scored = sorted(
            candidates, key=lambda d: self.mock_scorer(query, d.text), reverse=True
        )
        return scored[:top_k]

    def cost_overhead(self) -> dict[str, float]:
        return {"llm_calls": 0, "model_calls": 1, "latency_ms": 200.0}


@dataclass(frozen=True)
class ParentChildIndex:
    children: list[Document]
    parents: dict[str, Document]


class ParentChildChunker:
    """Indexa chunks pequeños; devuelve el contexto extendido (parent)."""

    def __init__(self, index: ParentChildIndex) -> None:
        self.index = index
        self.child_retriever = BaselineDenseRetriever(index.children)

    def retrieve(self, query: str, top_k: int = 5) -> list[Document]:
        children = self.child_retriever.retrieve(query, top_k=top_k)
        seen_parents: dict[str, Document] = {}
        for child in children:
            if child.parent_id and child.parent_id in self.index.parents:
                parent = self.index.parents[child.parent_id]
                if parent.doc_id not in seen_parents:
                    seen_parents[parent.doc_id] = parent
        return list(seen_parents.values())[:top_k]

    def cost_overhead(self) -> dict[str, float]:
        return {"llm_calls": 0, "model_calls": 0, "latency_ms": 50.0}


class SentenceWindowRetriever:
    """Indexa oraciones; devuelve la oración +/- window de contexto."""

    def __init__(self, sentences: list[str], window: int = 2) -> None:
        self.sentences = sentences
        self.window = window
        # Indexa cada oración como un Document
        self.docs = [Document(doc_id=f"sent_{i}", text=s) for i, s in enumerate(sentences)]
        self.retriever = BaselineDenseRetriever(self.docs)

    def retrieve(self, query: str, top_k: int = 5) -> list[Document]:
        hits = self.retriever.retrieve(query, top_k=top_k)
        results: list[Document] = []
        for hit in hits:
            idx = int(hit.doc_id.split("_")[1])
            lo = max(0, idx - self.window)
            hi = min(len(self.sentences), idx + self.window + 1)
            window_text = " ".join(self.sentences[lo:hi])
            results.append(Document(doc_id=hit.doc_id, text=window_text))
        return results

    def cost_overhead(self) -> dict[str, float]:
        return {"llm_calls": 0, "model_calls": 0, "latency_ms": 50.0}


@dataclass
class SelfRAGRetriever:
    """LLM decide cuándo recuperar y reflexiona sobre el resultado."""

    base: BaselineDenseRetriever
    should_retrieve: Callable[[str], bool]
    is_relevant: Callable[[str, Document], bool] = field(
        default=lambda q, d: True  # noqa: ARG005
    )

    def retrieve(self, query: str, top_k: int = 5) -> list[Document]:
        if not self.should_retrieve(query):
            return []
        candidates = self.base.retrieve(query, top_k=top_k * 2)
        filtered = [d for d in candidates if self.is_relevant(query, d)]
        return filtered[:top_k]

    def cost_overhead(self) -> dict[str, float]:
        return {"llm_calls": 2, "model_calls": 0, "latency_ms": 400.0}
