import pytest

from src.prompt_registry import PromptRegistry, build_default_registry
from src.regression_checker import RegressionChecker


@pytest.fixture(scope="module")
def registry() -> PromptRegistry:
    return build_default_registry()


@pytest.fixture
def checker() -> RegressionChecker:
    return RegressionChecker(threshold=0.1)
