from __future__ import annotations

import pytest

from src.simple_agent import SimpleAgent


@pytest.fixture
def agent() -> SimpleAgent:
    return SimpleAgent()
