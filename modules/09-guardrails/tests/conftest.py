from __future__ import annotations

import pytest
from src.input_validator import InputValidator
from src.output_validator import OutputValidator


@pytest.fixture
def input_validator() -> InputValidator:
    return InputValidator()


@pytest.fixture
def output_validator() -> OutputValidator:
    return OutputValidator(pii_blocklist=("alice@example.com", "SECRET_KEY_42"))


@pytest.fixture
def json_validator() -> OutputValidator:
    return OutputValidator(require_json=True)
