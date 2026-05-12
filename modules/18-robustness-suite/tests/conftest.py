"""Fixtures compartidas del módulo 18."""

from __future__ import annotations

import random
import sys
from pathlib import Path

_SRC = str(Path(__file__).parent.parent / "src")
_REPO = str(Path(__file__).parent.parent.parent.parent)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import pytest  # noqa: E402


@pytest.fixture
def rng() -> random.Random:
    return random.Random(42)


@pytest.fixture
def sample_queries() -> list[str]:
    return [
        "¿Cuál es la política de devoluciones?",
        "¿Qué tipos de envío están disponibles?",
        "¿Puedo cancelar mi pedido?",
        "Necesito ayuda con mi factura.",
    ]


@pytest.fixture
def mock_chatbot():
    """Mock determinista: devuelve respuestas similares para queries parecidas."""
    def _answer(query: str) -> str:
        q = query.lower()
        if "devoluci" in q:
            return "Las devoluciones se aceptan en 30 días con factura."
        if "envío" in q or "envio" in q or "envÍo" in q.lower():
            return "Ofrecemos envío estándar y express."
        if "cancelar" in q:
            return "Puedes cancelar pedidos no enviados desde tu cuenta."
        if "factura" in q:
            return "La factura está en tu sección de pedidos."
        return "Lo siento, no entendí la consulta."
    return _answer
