"""Fixtures compartidos para el módulo 01-primer-eval."""
from __future__ import annotations

import pytest

from src.simple_rag import SimpleRAG


@pytest.fixture(scope="module")
def rag() -> SimpleRAG:
    """Instancia del RAG bajo prueba, compartida por todos los tests del módulo."""
    return SimpleRAG()


@pytest.fixture
def returns_query() -> str:
    return "What is the return policy?"


@pytest.fixture
def shipping_query() -> str:
    return "How long does shipping take?"


@pytest.fixture
def hallucination_output() -> str:
    """Output que inventa información no presente en el knowledge base."""
    return (
        "You can return products within 365 days and get a 200% refund guaranteed. "
        "We offer same-day drone delivery to all countries for free."
    )
