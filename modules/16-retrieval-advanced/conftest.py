"""Configura sys.path para tests del módulo 16.

Mismo patrón que el módulo 14: inserta src/ directamente para evitar
colisiones del namespace `src` entre módulos. Imports en src/ y tests/ son
directos: `from retrieval_techniques import X`.
"""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = str(Path(__file__).parent / "src")
_REPO = str(Path(__file__).parent.parent.parent)

if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
