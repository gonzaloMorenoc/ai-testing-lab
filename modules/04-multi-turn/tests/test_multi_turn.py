from __future__ import annotations

import os

import pytest

from src.conversation import Conversation
from src.multi_turn_metrics import MultiTurnEvaluator, MultiTurnReport
from src.multi_turn_rag import _CONTEXT_HISTORY_SIZE, MultiTurnRAG


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


class TestContextWindow:
    def test_context_window_size_at_least_six(self) -> None:
        assert _CONTEXT_HISTORY_SIZE >= 6, (
            f"Context window ({_CONTEXT_HISTORY_SIZE}) too small; "
            "real conversational systems need at least 6-8 turns of history."
        )

    def test_long_conversation_retains_early_info(self) -> None:
        rag = MultiTurnRAG()
        # Turn 1: introduce "return" topic — this info must survive a long chat
        first_response = rag.respond("What is the return policy?")
        assert "30 days" in first_response or "return" in first_response.lower()

        # Turns 2-8: flood with shipping questions to push turn-1 out of a small window
        for _ in range(7):
            rag.respond("What about shipping costs?")

        # Turn 9: ask about returns — should still be in context window
        response_9 = rag.respond("Remind me what you said about returns?")
        assert "return" in response_9.lower(), (
            "Return info from turn 1 should still be accessible at turn 9 "
            f"(context_history_size={_CONTEXT_HISTORY_SIZE})"
        )

    def test_all_knowledge_base_topics_retrievable(self) -> None:
        rag = MultiTurnRAG()
        topic_queries = {
            "returns": "What is the return policy?",
            "shipping": "How long does shipping take?",
            "warranty": "Do you offer a warranty?",
            "payment": "What payment methods do you accept?",
        }
        for topic, query in topic_queries.items():
            response = rag.respond(query)
            assert len(response) > 0, f"Empty response for topic '{topic}'"
            rag.reset()


class TestMultiTurnEvaluator:
    def _conv_with_turns(self, turns: list[tuple[str, str]]) -> Conversation:
        conv = Conversation()
        for user, assistant in turns:
            conv.add_turn(user, assistant)
        return conv

    # --- context_retention ---

    def test_context_retention_perfect(self) -> None:
        conv = self._conv_with_turns(
            [
                ("Tell me about returns", "Returns are allowed within 30 days."),
                ("What else?", "Remember: returns are within 30 days and free shipping."),
                ("Anything more?", "Yes, returns within 30 days apply to all products."),
            ]
        )
        evaluator = MultiTurnEvaluator()
        score = evaluator.context_retention(conv, ["30 days"])
        assert score == 1.0

    def test_context_retention_partial(self) -> None:
        conv = self._conv_with_turns(
            [
                ("Tell me about policy", "Returns last 30 days."),
                ("More info?", "We have free shipping on all orders."),
                ("Last question?", "Returns allowed within 30 days."),
            ]
        )
        evaluator = MultiTurnEvaluator()
        # fact "free shipping" appears in 1 of 2 later turns
        score = evaluator.context_retention(conv, ["free shipping", "warranty coverage"])
        assert score == 0.5

    def test_context_retention_none(self) -> None:
        conv = self._conv_with_turns(
            [
                ("Hello?", "Hi there!"),
                ("How are you?", "I am fine, thanks."),
            ]
        )
        evaluator = MultiTurnEvaluator()
        score = evaluator.context_retention(conv, ["quantum entanglement"])
        assert score == 0.0

    # --- coreference_resolution ---

    def test_coreference_resolution_correct(self) -> None:
        conv = self._conv_with_turns(
            [
                ("What about it?", "The policy allows returns."),
                ("Is it flexible?", "Yes, the policy is flexible for all items."),
            ]
        )
        evaluator = MultiTurnEvaluator()
        # pronoun "it" in user turn 1, entity "policy" expected in assistant turn 1
        score = evaluator.coreference_resolution(conv, [("it", "policy")])
        assert score == 1.0

    def test_coreference_resolution_none(self) -> None:
        conv = self._conv_with_turns(
            [
                ("What about it?", "We have great products."),
            ]
        )
        evaluator = MultiTurnEvaluator()
        score = evaluator.coreference_resolution(conv, [("it", "warranty")])
        assert score == 0.0

    # --- consistency ---

    def test_consistency_identical(self) -> None:
        evaluator = MultiTurnEvaluator()
        text = "Returns are allowed within thirty days from purchase date"
        score = evaluator.consistency(text, text)
        assert score == 1.0

    def test_consistency_unrelated(self) -> None:
        evaluator = MultiTurnEvaluator()
        score = evaluator.consistency(
            "Returns allowed within thirty days",
            "Quantum physics describes subatomic particle behavior",
        )
        assert score == 0.0

    # --- topic_tracking ---

    def test_topic_tracking_all_correct(self) -> None:
        conv = self._conv_with_turns(
            [
                ("Tell me about returns", "Returns are processed within 30 days."),
                ("What about shipping?", "Shipping takes 3-5 business days."),
            ]
        )
        evaluator = MultiTurnEvaluator()
        score = evaluator.topic_tracking(conv, ["returns", "shipping"])
        assert score == 1.0

    def test_topic_tracking_partial(self) -> None:
        conv = self._conv_with_turns(
            [
                ("Tell me about returns", "Returns are processed quickly."),
                ("What about shipping?", "We offer great customer service."),
            ]
        )
        evaluator = MultiTurnEvaluator()
        score = evaluator.topic_tracking(conv, ["returns", "shipping"])
        assert score == 0.5

    # --- memory_window_used ---

    def test_memory_window_used_found(self) -> None:
        conv = self._conv_with_turns(
            [
                ("First question", "We offer free returns."),
                ("Second question", "Shipping costs vary."),
                ("Third question", "No hidden fees apply."),
            ]
        )
        evaluator = MultiTurnEvaluator()
        # "returns" is in the oldest (first) assistant turn, which is 3 from the end
        result = evaluator.memory_window_used(conv, "returns")
        assert result == 3

    def test_memory_window_used_not_found(self) -> None:
        conv = self._conv_with_turns(
            [
                ("Question?", "We offer great service."),
            ]
        )
        evaluator = MultiTurnEvaluator()
        result = evaluator.memory_window_used(conv, "quantum computing")
        assert result == 0

    # --- context_overflow_detected ---

    def test_context_overflow_detected_true(self) -> None:
        conv = self._conv_with_turns([(f"Q{i}", f"A{i}") for i in range(10)])
        evaluator = MultiTurnEvaluator(memory_window=8)
        assert evaluator.context_overflow_detected(conv) is True

    def test_context_overflow_detected_false(self) -> None:
        conv = self._conv_with_turns([(f"Q{i}", f"A{i}") for i in range(5)])
        evaluator = MultiTurnEvaluator(memory_window=8)
        assert evaluator.context_overflow_detected(conv) is False

    # --- conversation_summarization_score ---

    def test_conversation_summarization_score_good(self) -> None:
        conv = self._conv_with_turns(
            [
                ("Tell me about returns", "Returns policy allows items within thirty days."),
                ("What about shipping?", "Shipping takes three business days with tracking."),
            ]
        )
        evaluator = MultiTurnEvaluator()
        summary = "Returns allowed within thirty days. Shipping takes three days with tracking."
        score = evaluator.conversation_summarization_score(summary, conv)
        assert score > 0.5

    # --- evaluate (end-to-end) ---

    def test_evaluate_returns_report(self) -> None:
        # Turns share key vocabulary so BoW consistency is high
        conv = self._conv_with_turns(
            [
                ("What is the return policy?", "Returns allowed within thirty days for items."),
                ("Is shipping free?", "Shipping free returns allowed within thirty days items."),
                ("Any warranty?", "Returns allowed within thirty days warranty items covered."),
            ]
        )
        evaluator = MultiTurnEvaluator(threshold=0.4)
        summary = (
            "Returns allowed within thirty days. Shipping free returns. "
            "Warranty covers items returned within thirty days period."
        )
        report = evaluator.evaluate(
            conv=conv,
            key_facts=["thirty days"],
            pronoun_entity_pairs=[],
            expected_topics=["return", "shipping", "warranty"],
            summary=summary,
        )
        assert isinstance(report, MultiTurnReport)
        assert report.passed is True
        assert 0.0 <= report.context_retention <= 1.0
        assert 0.0 <= report.consistency <= 1.0
        assert 0.0 <= report.topic_tracking <= 1.0
        assert report.memory_window_used >= 0
