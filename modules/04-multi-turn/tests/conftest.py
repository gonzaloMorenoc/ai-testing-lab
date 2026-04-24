import pytest
from src.conversation import Conversation
from src.multi_turn_rag import MultiTurnRAG


@pytest.fixture
def conversation() -> Conversation:
    return Conversation()


@pytest.fixture
def rag() -> MultiTurnRAG:
    return MultiTurnRAG()
