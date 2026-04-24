from __future__ import annotations

import pytest

from src import tracer as tracer_module
from src.mock_collector import MockCollector


@pytest.fixture
def collector() -> MockCollector:
    coll = MockCollector()
    tracer_module.set_collector(coll)
    yield coll
    coll.clear()
    tracer_module.set_collector(None)  # type: ignore[arg-type]
