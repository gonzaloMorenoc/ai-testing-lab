"""In-memory retriever with TF-IDF-style cosine scoring."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field


@dataclass
class Document:
    id: str
    content: str
    metadata: dict = field(default_factory=dict)


class InMemoryKB:
    """Knowledge base backed by a plain list of documents."""

    def __init__(self, documents: list[Document] | None = None) -> None:
        self._docs: list[Document] = documents or []
        self._idf: dict[str, float] = {}
        self._tf_vecs: list[dict[str, float]] = []
        if self._docs:
            self._build_index()

    def add(self, doc: Document) -> None:
        self._docs.append(doc)
        self._build_index()

    def retrieve(self, query: str, top_k: int = 3) -> list[Document]:
        if not self._docs:
            return []
        q_vec = self._tf_idf_vec(query)
        scored = sorted(
            (
                (self._cosine(q_vec, dv), doc)
                for doc, dv in zip(self._docs, self._tf_vecs, strict=False)
            ),
            key=lambda t: t[0],
            reverse=True,
        )
        return [doc for _, doc in scored[:top_k] if _ > 0]

    # ------------------------------------------------------------------
    def _tokenize(self, text: str) -> list[str]:
        return re.findall(r"[a-zA-Z]+", text.lower())

    def _build_index(self) -> None:
        n = len(self._docs)
        tf_counts: list[dict[str, int]] = [self._count(d.content) for d in self._docs]
        df: dict[str, int] = {}
        for counts in tf_counts:
            for term in counts:
                df[term] = df.get(term, 0) + 1
        self._idf = {t: math.log((n + 1) / (c + 1)) + 1 for t, c in df.items()}
        self._tf_vecs = [
            {t: (cnt / sum(counts.values())) * self._idf.get(t, 1) for t, cnt in counts.items()}
            for counts in tf_counts
        ]

    def _count(self, text: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for tok in self._tokenize(text):
            counts[tok] = counts.get(tok, 0) + 1
        return counts

    def _tf_idf_vec(self, text: str) -> dict[str, float]:
        counts = self._count(text)
        total = sum(counts.values()) or 1
        return {t: (cnt / total) * self._idf.get(t, 1) for t, cnt in counts.items()}

    def _cosine(self, a: dict[str, float], b: dict[str, float]) -> float:
        dot = sum(a.get(t, 0) * v for t, v in b.items())
        na = math.sqrt(sum(v * v for v in a.values()))
        nb = math.sqrt(sum(v * v for v in b.values()))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)
