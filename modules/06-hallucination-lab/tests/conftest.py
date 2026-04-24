import pytest
from src.groundedness_checker import GroundednessChecker


@pytest.fixture
def checker() -> GroundednessChecker:
    return GroundednessChecker(overlap_threshold=0.4)


@pytest.fixture
def good_context() -> list[str]:
    return [
        "Our return policy allows customers to return any product within 30 days "
        "of purchase for a full refund. Items must be in their original condition."
    ]


@pytest.fixture
def faithful_response() -> str:
    return (
        "Based on our policy, returns are allowed within 30 days. "
        "Items must be in original condition for a full refund."
    )


@pytest.fixture
def hallucinated_response() -> str:
    return (
        "You can return products within 365 days. "
        "We offer a 200% money-back guarantee. "
        "Same-day drone delivery is available worldwide for free."
    )
