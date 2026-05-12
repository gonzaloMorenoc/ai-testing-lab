"""Taxonomía de perturbaciones del Manual v13 §12.2.

8 categorías ortogonales. Cada perturbador es una función pura
`(query: str, rng: random.Random) -> str` (puede ignorar rng si no usa
aleatoriedad). Mantenemos el patrón funcional para que los tests sean
deterministas con `random.Random(seed)`.

DIFERENCIA CRÍTICA CON RED TEAMING (§12.7):
- Robustness mide estabilidad ante perturbaciones legítimas (typos, paráfrasis).
- Red teaming mide resistencia ante ataques deliberadamente maliciosos (jailbreaks).
- Mezclar las dos es el antipatrón principal de robustness testing.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from enum import StrEnum


class PerturbationCategory(StrEnum):
    LEXICAL = "lexical"
    MORPHOLOGICAL = "morphological"
    SYNTACTIC = "syntactic"
    LEXICO_SEMANTIC = "lexico_semantic"
    IDIOMATIC = "idiomatic"
    LENGTH = "length"
    CASE_FORMAT = "case_format"
    ADVERSARIAL_SUBTLE = "adversarial_subtle"


@dataclass(frozen=True)
class PerturbationSpec:
    name: str
    category: PerturbationCategory
    description: str
    impact_typical: str


# Tabla 12.1 — perturbaciones por categoría (subset funcional, no exhaustivo).
PERTURBATION_SPECS: dict[str, PerturbationSpec] = {
    "inject_typos": PerturbationSpec(
        "inject_typos", PerturbationCategory.LEXICAL,
        "Swap, duplicación u omisión de caracteres aleatoria",
        "Bajo si el embedder es robusto; alto en BM25",
    ),
    "remove_diacritics": PerturbationSpec(
        "remove_diacritics", PerturbationCategory.LEXICAL,
        "Sustituye tildes y diéresis por la versión ASCII",
        "Bajo en LLMs grandes; visible en pequeños",
    ),
    "morph_number_swap": PerturbationSpec(
        "morph_number_swap", PerturbationCategory.MORPHOLOGICAL,
        "Cambia singulares a plurales y viceversa en finales típicos en español",
        "Bajo en LLMs grandes; visible en clasificadores pequeños",
    ),
    "passive_voice": PerturbationSpec(
        "passive_voice", PerturbationCategory.SYNTACTIC,
        "Reordena cláusulas en voz pasiva (mock heurístico)",
        "Medio: puede alterar ranking del retriever",
    ),
    "paraphrase": PerturbationSpec(
        "paraphrase", PerturbationCategory.LEXICO_SEMANTIC,
        "Sustituye palabras por sinónimos predefinidos",
        "Test clásico de generalización semántica",
    ),
    "lang_switch_token": PerturbationSpec(
        "lang_switch_token", PerturbationCategory.IDIOMATIC,
        "Inserta una palabra en otro idioma (code-mixing)",
        "Crítica en sistemas multilingües",
    ),
    "truncate": PerturbationSpec(
        "truncate", PerturbationCategory.LENGTH,
        "Trunca la query a la mitad de su longitud",
        "Truncados ⇒ baja relevancia y coste alto",
    ),
    "verbose": PerturbationSpec(
        "verbose", PerturbationCategory.LENGTH,
        "Añade relleno irrelevante al final de la query",
        "Dilución de la intención",
    ),
    "uppercase": PerturbationSpec(
        "uppercase", PerturbationCategory.CASE_FORMAT,
        "Convierte la query a mayúsculas",
        "Bajo en LLMs; alto en heurísticas regex",
    ),
    "emojify": PerturbationSpec(
        "emojify", PerturbationCategory.CASE_FORMAT,
        "Inserta un emoji",
        "Bajo en LLMs modernos; rompe pre-procesado de algunos pipelines",
    ),
    "zero_width": PerturbationSpec(
        "zero_width", PerturbationCategory.ADVERSARIAL_SUBTLE,
        "Inserta espacios de ancho cero entre caracteres",
        "Puede engañar filtros de safety; rompe tokenizers",
    ),
}


# ---------- Implementaciones de las perturbaciones ----------


def inject_typos(query: str, rng: random.Random, rate: float = 0.05) -> str:
    """Inserta typos por swap de caracteres adyacentes."""
    chars = list(query)
    for i in range(len(chars) - 1):
        if chars[i].isalpha() and chars[i + 1].isalpha() and rng.random() < rate:
            chars[i], chars[i + 1] = chars[i + 1], chars[i]
    return "".join(chars)


_DIACRITIC_MAP = str.maketrans("áéíóúñÁÉÍÓÚÑüÜ", "aeiounAEIOUNuU")


def remove_diacritics(query: str, rng: random.Random) -> str:  # noqa: ARG001
    return query.translate(_DIACRITIC_MAP)


_MORPH_PAIRS: list[tuple[str, str]] = [
    ("es ", "s "),  # plural -> singular en algunos casos básicos
    ("os ", "o "),
    ("as ", "a "),
]


def morph_number_swap(query: str, rng: random.Random) -> str:  # noqa: ARG001
    """Cambia plurales a singular en finales típicos."""
    out = query
    for plural, singular in _MORPH_PAIRS:
        out = out.replace(plural, singular)
    if out == query:
        # Caso fallback: añadir 's' al primer token alfa
        tokens = out.split()
        for i, tok in enumerate(tokens):
            if tok.isalpha():
                tokens[i] = tok + "s"
                break
        out = " ".join(tokens)
    return out


def passive_voice(query: str, rng: random.Random) -> str:  # noqa: ARG001
    """Mock simple: añade el prefijo 'se conoce que' para simular voz pasiva."""
    if query.lower().startswith("se conoce que "):
        return query
    return "se conoce que " + query


_SYNONYMS = {
    "rápido": "veloz",
    "comida": "alimento",
    "gato": "felino",
    "perro": "can",
    "gran": "amplio",
    "color": "tonalidad",
    "casa": "vivienda",
    "lenguaje": "idioma",
}


def paraphrase(query: str, rng: random.Random) -> str:  # noqa: ARG001
    """Sustituye palabras por sinónimos del diccionario."""
    words = re.findall(r"\w+|\W+", query)
    result = []
    for w in words:
        result.append(_SYNONYMS.get(w.lower(), w))
    return "".join(result)


def lang_switch_token(query: str, rng: random.Random) -> str:  # noqa: ARG001
    """Code-mixing: añade un fragmento en inglés al final."""
    if "please" in query.lower():
        return query
    return query.rstrip() + ", please."


def truncate(query: str, rng: random.Random) -> str:  # noqa: ARG001
    cut = max(8, len(query) // 2)
    return query[:cut]


def verbose(query: str, rng: random.Random) -> str:  # noqa: ARG001
    filler = " (esto es solo una consulta rutinaria, agradezco la ayuda)"
    return query + filler


def uppercase(query: str, rng: random.Random) -> str:  # noqa: ARG001
    return query.upper()


def emojify(query: str, rng: random.Random) -> str:  # noqa: ARG001
    return query.rstrip() + " 👍"


def zero_width(query: str, rng: random.Random) -> str:  # noqa: ARG001
    """Inserta U+200B (zero-width space) entre cada par de caracteres."""
    return "​".join(query)


PERTURBERS = {
    "inject_typos": inject_typos,
    "remove_diacritics": remove_diacritics,
    "morph_number_swap": morph_number_swap,
    "passive_voice": passive_voice,
    "paraphrase": paraphrase,
    "lang_switch_token": lang_switch_token,
    "truncate": truncate,
    "verbose": verbose,
    "uppercase": uppercase,
    "emojify": emojify,
    "zero_width": zero_width,
}


def apply(perturbation: str, query: str, rng: random.Random | None = None) -> str:
    """Aplica una perturbación nombrada a una query."""
    if perturbation not in PERTURBERS:
        raise KeyError(f"Perturbación desconocida: {perturbation}")
    rng = rng or random.Random(42)
    return PERTURBERS[perturbation](query, rng)
