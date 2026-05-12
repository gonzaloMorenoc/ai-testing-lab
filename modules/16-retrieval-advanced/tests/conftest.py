"""Fixtures compartidas del módulo 16."""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = str(Path(__file__).parent.parent / "src")
_REPO = str(Path(__file__).parent.parent.parent.parent)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import pytest  # noqa: E402

from retrieval_techniques import BaselineDenseRetriever, Document  # noqa: E402


@pytest.fixture
def sample_docs() -> list[Document]:
    return [
        Document("d1", "El gato negro come pescado fresco todas las mañanas."),
        Document("d2", "Los perros corren rápido en el parque al atardecer."),
        Document("d3", "La inteligencia artificial transforma la industria del software."),
        Document("d4", "El gato pardo duerme en el sofá durante la tarde."),
        Document("d5", "Python es un lenguaje de programación versátil para data science."),
        Document("d6", "La paella valenciana lleva arroz bomba y azafrán."),
        Document("d7", "Los modelos LLM grandes requieren mucha memoria GPU."),
        Document("d8", "El gato gris caza ratones en el jardín por la noche."),
    ]


@pytest.fixture
def baseline_retriever(sample_docs) -> BaselineDenseRetriever:
    return BaselineDenseRetriever(sample_docs)


@pytest.fixture
def qrels_by_query() -> dict[str, dict[str, float]]:
    """Cada query con sus documentos relevantes y grado de relevancia."""
    return {
        "gato come": {"d1": 2.0, "d4": 1.0, "d8": 1.0},
        "lenguaje programacion": {"d5": 2.0, "d7": 1.0},
        "comida valenciana": {"d6": 2.0},
    }
