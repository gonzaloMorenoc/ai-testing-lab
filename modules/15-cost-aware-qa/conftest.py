"""Configura sys.path para tests del módulo 15.

Patrón del módulo 14: inserta src/ directamente en sys.path para evitar
colisiones del paquete `src` cuando pytest carga varios módulos del repo a
la vez. Los imports en src/ y tests/ son directos: `from cost_metrics import X`.

También inserta la raíz del repo para `from qa_thresholds import ...`
(Tabla 4.2 del Manual v13).
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
