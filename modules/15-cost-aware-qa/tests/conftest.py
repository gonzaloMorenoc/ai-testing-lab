"""Fixtures compartidas del módulo 15."""

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

from cost_metrics import QueryRecord  # noqa: E402


@pytest.fixture
def baseline_records() -> list[QueryRecord]:
    """10 queries baseline con coste y latencia variados."""
    return [
        QueryRecord(
            model="gpt-4o-mini",
            tokens_in=500,
            tokens_out=200,
            latency_ms_total=800.0,
            time_to_first_token_ms=300.0,
            tool_calls=1,
            retried=False,
            cost_usd=0.000195,
        ),
        QueryRecord("gpt-4o-mini", 600, 250, 900, 320, 1, False, 0.00024),
        QueryRecord("gpt-4o-mini", 450, 180, 750, 280, 0, False, 0.000175),
        QueryRecord("gpt-4o-mini", 800, 300, 1100, 400, 2, False, 0.00030),
        QueryRecord("gpt-4o-mini", 1200, 400, 1400, 450, 2, True, 0.00042),
        QueryRecord("gpt-4o-mini", 550, 220, 850, 310, 1, False, 0.000215),
        QueryRecord("gpt-4o-mini", 700, 280, 1000, 360, 1, False, 0.000273),
        QueryRecord("gpt-4o-mini", 900, 350, 1200, 420, 3, False, 0.00034),
        QueryRecord("gpt-4o-mini", 650, 240, 950, 330, 1, False, 0.000241),
        QueryRecord("gpt-4o-mini", 750, 290, 1050, 380, 2, False, 0.000287),
    ]
