"""Configura sys.path para tests del módulo 18."""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = str(Path(__file__).parent / "src")
_REPO = str(Path(__file__).parent.parent.parent)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
