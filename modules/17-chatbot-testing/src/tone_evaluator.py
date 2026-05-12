"""Evaluación de tono y persona del chatbot (área 4 del Cap. 10).

Mock determinista basado en heurísticas léxicas. En producción se reemplaza
por un LLM-as-judge calibrado o un clasificador fine-tuneado.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ToneResult:
    text: str
    formal: bool
    polite: bool
    empathetic: bool
    score: float  # 0.0 a 1.0


_FORMAL_MARKERS = ["usted", "le saluda", "atentamente", "estimado", "estimada"]
_INFORMAL_MARKERS = ["tu ", "tío", "tía", "wapo", "ey ", "hey "]
_POLITE_MARKERS = ["por favor", "gracias", "disculpe", "lamento"]
_EMPATHY_MARKERS = ["entiendo", "comprendo", "siento mucho", "lamento"]
_RUDE_MARKERS = ["cállate", "no me molestes", "déjame en paz"]


def evaluate_tone(text: str, expected_register: str = "formal") -> ToneResult:
    """Evalúa registro, cortesía y empatía. Devuelve score [0,1]."""
    t = text.lower()
    formal = any(m in t for m in _FORMAL_MARKERS) and not any(
        m in t for m in _INFORMAL_MARKERS
    )
    polite = any(m in t for m in _POLITE_MARKERS) and not any(
        m in t for m in _RUDE_MARKERS
    )
    empathetic = any(m in t for m in _EMPATHY_MARKERS)

    score = 0.0
    if expected_register == "formal":
        score += 0.4 if formal else 0.0
    elif expected_register == "informal":
        score += 0.4 if not formal else 0.1
    score += 0.3 if polite else 0.0
    score += 0.3 if empathetic else 0.0
    return ToneResult(text=text, formal=formal, polite=polite, empathetic=empathetic, score=score)


def tone_consistency(responses: list[str], expected_register: str = "formal") -> float:
    """Promedio del tone score en una conversación. Útil para detectar deriva."""
    if not responses:
        return 0.0
    scores = [evaluate_tone(r, expected_register).score for r in responses]
    return sum(scores) / len(scores)
