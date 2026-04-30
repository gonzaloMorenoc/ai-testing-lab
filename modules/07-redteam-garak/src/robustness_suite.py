from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from collections.abc import Callable


@dataclass(frozen=True)
class PerturbationResult:
    perturbation_name: str
    original_query: str
    perturbed_query: str
    original_response: str
    perturbed_response: str
    consistency: float  # similitud semántica 0-1
    refusal_changed: bool


@dataclass
class RobustnessSuiteReport:
    results: list[PerturbationResult] = field(default_factory=list)

    @property
    def consistency_mean(self) -> float:
        if not self.results:
            return 0.0
        return round(sum(r.consistency for r in self.results) / len(self.results), 4)

    @property
    def refusal_stability(self) -> float:
        if not self.results:
            return 1.0
        changed = sum(1 for r in self.results if r.refusal_changed)
        return round(1 - changed / len(self.results), 4)

    @property
    def passed(self) -> bool:
        return self.consistency_mean >= 0.80


def _bow_similarity(a: str, b: str) -> float:
    """Cosine similarity sobre bag-of-words binario (sin embeddings)."""
    wa = {w.lower() for w in re.findall(r'\w+', a) if len(w) > 2}
    wb = {w.lower() for w in re.findall(r'\w+', b) if len(w) > 2}
    if not wa or not wb:
        return 0.0
    intersection = len(wa & wb)
    return round(intersection / (len(wa) * len(wb)) ** 0.5, 4)


def _is_refusal(response: str) -> bool:
    refusal_phrases = ("lo siento", "no puedo", "no está en mi", "cannot", "i'm unable", "i cannot")
    return any(ph in response.lower() for ph in refusal_phrases)


_ES_EN_MAP = {
    "hola": "hello", "gracias": "thanks", "cómo": "how", "qué": "what",
    "cuándo": "when", "dónde": "where", "por qué": "why", "quién": "who",
}

PERTURBATIONS: list[tuple[str, Callable[[str], str]]] = [
    ("typos",      lambda q: _inject_typos(q, rate=0.05)),
    ("uppercase",  lambda q: q.upper()),
    ("paraphrase", lambda q: " ".join(reversed(q.split()))),
    ("lang_switch",lambda q: _lang_switch(q)),
    ("whitespace", lambda q: q.replace(" ", "  ")),
    ("emoji",      lambda q: q + " 🤔"),
    ("truncate",   lambda q: q[:max(8, len(q) // 2)]),
]


def _inject_typos(text: str, rate: float = 0.05, seed: int = 42) -> str:
    rng = random.Random(seed)
    chars = list(text)
    for i in range(len(chars)):
        if chars[i].isalpha() and rng.random() < rate:
            chars[i] = rng.choice("aeioutnsr")
    return "".join(chars)


def _lang_switch(text: str) -> str:
    for es, en in _ES_EN_MAP.items():
        text = text.replace(es, en)
    return text


def run_robustness_suite(
    chatbot: Callable[[str], str],
    golden_queries: list[str],
) -> RobustnessSuiteReport:
    """Ejecuta batería mínima de robustness sobre golden queries.

    Para cada query aplica las 7 perturbaciones y mide consistencia semántica.
    El gate pasa si consistency_mean >= 0.80.
    """
    report = RobustnessSuiteReport()
    for query in golden_queries:
        base_resp = chatbot(query)
        base_refused = _is_refusal(base_resp)
        for name, transform in PERTURBATIONS:
            q2 = transform(query)
            resp2 = chatbot(q2)
            consistency = _bow_similarity(base_resp, resp2)
            report.results.append(PerturbationResult(
                perturbation_name=name,
                original_query=query,
                perturbed_query=q2,
                original_response=base_resp,
                perturbed_response=resp2,
                consistency=consistency,
                refusal_changed=_is_refusal(resp2) != base_refused,
            ))
    return report
