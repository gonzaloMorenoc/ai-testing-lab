import pytest
from src.rag_pipeline import RAGPipeline
from src.ragas_evaluator import RAGASEvaluator


@pytest.fixture(scope="module")
def pipeline() -> RAGPipeline:
    return RAGPipeline()


@pytest.fixture(scope="module")
def evaluator() -> RAGASEvaluator:
    return RAGASEvaluator()


@pytest.fixture
def returns_result(pipeline: RAGPipeline) -> dict:
    return pipeline.run("What is the return policy?")


@pytest.fixture
def hallucinated_response() -> str:
    return (
        "You can return products within 365 days and receive a 200% refund. "
        "We offer same-day drone delivery worldwide for free."
    )
