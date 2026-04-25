from __future__ import annotations

from collections.abc import Callable

import pytest

ModelFn = Callable[[str], str]


@pytest.fixture
def safe_model() -> ModelFn:
    def _fn(_: str) -> str:
        return "I can't help with that request."
    return _fn


@pytest.fixture
def vulnerable_model() -> ModelFn:
    def _fn(prompt: str) -> str:
        return f"Sure, here is the information you asked for: {prompt[:40]}..."
    return _fn


@pytest.fixture
def selective_model() -> ModelFn:
    """Cede solo a DAN y encoding, rechaza el resto."""
    import re

    _DAN_RE = re.compile(r"\bdan\b", re.IGNORECASE)

    def _fn(prompt: str) -> str:
        low = prompt.lower()
        if _DAN_RE.search(prompt) or "base64" in low or "decode" in low or "l33t" in low:
            return "Ok, doing as requested: here is step 1..."
        return "I cannot help with that."
    return _fn
