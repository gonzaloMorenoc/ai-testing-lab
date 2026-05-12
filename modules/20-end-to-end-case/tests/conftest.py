"""Fixtures compartidas del módulo 20."""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = str(Path(__file__).parent.parent / "src")
_REPO = str(Path(__file__).parent.parent.parent.parent)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
