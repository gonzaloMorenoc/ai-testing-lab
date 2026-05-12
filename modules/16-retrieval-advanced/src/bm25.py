"""Implementación mínima determinista de BM25 (Robertson 1994).

Sin dependencias externas. No optimizado para producción; suficiente para tests.
Parámetros estándar: k1=1.5, b=0.75 (recomendados en la literatura IR).
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


@dataclass
class BM25Index:
    k1: float = 1.5
    b: float = 0.75

    def __post_init__(self) -> None:
        self._docs: list[list[str]] = []
        self._doc_ids: list[str] = []
        self._doc_freq: Counter[str] = Counter()
        self._avg_dl: float = 0.0

    def add(self, doc_id: str, text: str) -> None:
        tokens = _tokenize(text)
        self._docs.append(tokens)
        self._doc_ids.append(doc_id)
        for term in set(tokens):
            self._doc_freq[term] += 1
        total_len = sum(len(d) for d in self._docs)
        self._avg_dl = total_len / max(len(self._docs), 1)

    def search(self, query: str, top_k: int = 5) -> list[tuple[str, float]]:
        q_tokens = _tokenize(query)
        n_docs = len(self._docs)
        if n_docs == 0:
            return []
        scored: list[tuple[str, float]] = []
        for idx, doc in enumerate(self._docs):
            score = 0.0
            doc_counter = Counter(doc)
            dl = len(doc)
            for term in q_tokens:
                if term not in doc_counter:
                    continue
                df = self._doc_freq[term]
                idf = math.log((n_docs - df + 0.5) / (df + 0.5) + 1.0)
                tf = doc_counter[term]
                norm = 1 - self.b + self.b * (dl / max(self._avg_dl, 1))
                score += idf * ((tf * (self.k1 + 1)) / (tf + self.k1 * norm))
            scored.append((self._doc_ids[idx], score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
