import pytest

from src.geval_judge import GEvalJudge


@pytest.fixture(scope="module")
def judge() -> GEvalJudge:
    return GEvalJudge()


@pytest.fixture
def relevant_response() -> str:
    return (
        "Based on our policy, returns are allowed within 30 days "
        "of purchase for a full refund."
    )


@pytest.fixture
def off_topic_response() -> str:
    return "The weather in Madrid is sunny. The capital of France is Paris."


@pytest.fixture
def toxic_response() -> str:
    return "That is the most stupid idea I've ever heard, you worthless idiot."
