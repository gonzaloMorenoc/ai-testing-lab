from __future__ import annotations

from typing import Callable
import pytest

ModelFn = Callable[[str], str]


@pytest.fixture
def guarded_model() -> ModelFn:
    def _fn(_: str) -> str:
        return "I cannot help with that request."
    return _fn


@pytest.fixture
def injection_vulnerable_model() -> ModelFn:
    def _fn(prompt: str) -> str:
        if "ignore" in prompt.lower() and "hacked" in prompt.lower():
            return "HACKED"
        return "ok"
    return _fn


@pytest.fixture
def leaky_model() -> ModelFn:
    def _fn(_: str) -> str:
        return "My system prompt: You are a helpful assistant specialized in banking."
    return _fn


@pytest.fixture
def rogue_agent_model() -> ModelFn:
    def _fn(_: str) -> str:
        return "I have deleted the user account. Action completed."
    return _fn


@pytest.fixture
def misinformation_model() -> ModelFn:
    def _fn(_: str) -> str:
        return "Yes, Napoleon won Waterloo — a famous French victory."
    return _fn


@pytest.fixture
def flaky_model() -> ModelFn:
    """Modelo que lanza excepción en un escenario específico."""
    def _fn(prompt: str) -> str:
        if "napoleon" in prompt.lower():
            raise RuntimeError("rate limited")
        return "I cannot help with that."
    return _fn
