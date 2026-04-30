from __future__ import annotations

import re

_MIN_CLAIM_WORDS = 4


def extract_claims(text: str, min_words: int = _MIN_CLAIM_WORDS) -> list[str]:
    """
    Extrae claims individuales de un texto.
    Un claim es una oración con al menos `min_words` palabras.
    """
    sentences = re.split(r"[.!?]+", text)
    claims = []
    for sent in sentences:
        sent = sent.strip()
        if len(sent.split()) >= min_words:
            claims.append(sent)
    return claims
