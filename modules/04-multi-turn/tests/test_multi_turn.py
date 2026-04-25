from __future__ import annotations

import os

import pytest

from src.conversation import Conversation
from src.multi_turn_rag import MultiTurnRAG


class TestConversation:

    def test_add_turn_stores_both_messages(self, conversation: Conversation) -> None:
        conversation.add_turn("Hello", "Hi there!")
        assert conversation.num_turns() == 1
        assert len(conversation.messages) == 2

    def test_info_retained_from_turn_1_in_turn_3(self, rag: MultiTurnRAG) -> None:
        rag.respond("What is the return policy?")
        rag.respond("And what about shipping?")
        response_3 = rag.respond("Can you summarize what you told me?")
        assert "30 days" in response_3 or "return" in response_3.lower(), (
            "Info from turn 1 should still be accessible in turn 3"
        )

    def test_conversation_num_turns(self, conversation: Conversation) -> None:
        conversation.add_turn("Q1", "A1")
        conversation.add_turn("Q2", "A2")
        conversation.add_turn("Q3", "A3")
        assert conversation.num_turns() == 3

    def test_reset_clears_history(self, rag: MultiTurnRAG) -> None:
        rag.respond("What is the return policy?")
        assert rag.conversation.num_turns() == 1
        rag.reset()
        assert rag.conversation.num_turns() == 0

    def test_contains_info_detects_keyword(self, conversation: Conversation) -> None:
        conversation.add_turn("Q", "Returns are allowed within 30 days.")
        assert conversation.contains_info("30 days")
        assert not conversation.contains_info("365 days")

    def test_detect_contradiction_found(self, conversation: Conversation) -> None:
        conversation.add_turn("How long?", "Returns allowed within 30 days.")
        conversation.add_turn("Really?", "Actually it's 60 days for premium.")
        assert conversation.detect_contradiction("days", "30", "60")

    def test_detect_contradiction_not_found(self, conversation: Conversation) -> None:
        conversation.add_turn("How long?", "Returns allowed within 30 days.")
        assert not conversation.detect_contradiction("days", "30", "60")

    def test_deepeval_format_structure(self, conversation: Conversation) -> None:
        conversation.add_turn("Q", "A")
        fmt = conversation.to_deepeval_format()
        assert len(fmt) == 2
        assert fmt[0]["role"] == "user"
        assert fmt[1]["role"] == "assistant"
        assert "content" in fmt[0]

    def test_five_turn_conversation_coherent(self, rag: MultiTurnRAG) -> None:
        topics = [
            "What is the return policy?",
            "What about shipping?",
            "Do you offer warranty?",
            "What payment methods?",
            "Can I return a digital product?",
        ]
        responses = [rag.respond(q) for q in topics]
        assert all(r for r in responses), "All responses should be non-empty"
        assert rag.conversation.num_turns() == 5

    def test_knowledge_retention_mock(self, rag: MultiTurnRAG) -> None:
        rag.respond("What is the return policy?")
        rag.respond("What about shipping costs?")
        response = rag.respond("What did you say about returns?")
        retained = "return" in response.lower() or "30 days" in response
        print(f"\n  Knowledge retained: {retained}")
        assert retained, "RAG should retain information about returns in turn 3"

    @pytest.mark.slow
    def test_with_real_deepeval_conversational(self, rag: MultiTurnRAG) -> None:
        if not os.getenv("GROQ_API_KEY"):
            pytest.skip("GROQ_API_KEY no encontrado")
        from deepeval.metrics import KnowledgeRetentionMetric
        from deepeval.test_case import ConversationalTestCase, LLMTestCase

        rag.respond("What is the return policy?")
        rag.respond("And shipping?")
        messages = rag.conversation.to_deepeval_format()
        tc = ConversationalTestCase(
            messages=[
                LLMTestCase(input=m["content"], actual_output="")
                if m["role"] == "user"
                else LLMTestCase(input="", actual_output=m["content"])
                for m in messages
            ]
        )
        metric = KnowledgeRetentionMetric(threshold=0.5)
        metric.measure(tc)
        print(f"\n  KnowledgeRetention: {metric.score}")
        assert metric.is_successful()
