from __future__ import annotations

import math
from dataclasses import dataclass

from src.conversation import Conversation

MULTI_TURN_THRESHOLD = 0.70


@dataclass(frozen=True)
class MultiTurnReport:
    context_retention: float
    coreference_resolution: float
    consistency: float
    topic_tracking: float
    memory_window_used: int
    context_overflow_detected: bool
    conversation_summarization_score: float
    passed: bool


def _bow_cosine(text_a: str, text_b: str) -> float:
    words_a = set(w.lower() for w in text_a.split() if len(w) > 3)
    words_b = set(w.lower() for w in text_b.split() if len(w) > 3)
    if not words_a or not words_b:
        return 0.0
    intersection = len(words_a & words_b)
    return round(intersection / math.sqrt(len(words_a) * len(words_b)), 4)


class MultiTurnEvaluator:
    def __init__(self, memory_window: int = 8, threshold: float = MULTI_TURN_THRESHOLD) -> None:
        self._memory_window = memory_window
        self._threshold = threshold

    def context_retention(self, conv: Conversation, key_facts: list[str]) -> float:
        """Fraction of key_facts that appear in assistant turns after the first one."""
        assistant_turns = conv.get_assistant_turns()
        later_turns = assistant_turns[1:]
        if not key_facts or not later_turns:
            return 0.0
        full_text = " ".join(later_turns).lower()
        found = sum(1 for fact in key_facts if fact.lower() in full_text)
        return round(found / len(key_facts), 4)

    def coreference_resolution(
        self,
        conv: Conversation,
        pronoun_entity_pairs: list[tuple[str, str]],
    ) -> float:
        """Fraction of (pronoun, entity) pairs correctly resolved in the next assistant turn."""
        if not pronoun_entity_pairs:
            return 1.0
        user_turns = conv.get_user_turns()
        assistant_turns = conv.get_assistant_turns()
        resolved = 0
        for pronoun, entity in pronoun_entity_pairs:
            pronoun_lower = pronoun.lower()
            entity_lower = entity.lower()
            for i, user_turn in enumerate(user_turns):
                if pronoun_lower in user_turn.lower() and i < len(assistant_turns):
                    if entity_lower in assistant_turns[i].lower():
                        resolved += 1
                    break
        return round(resolved / len(pronoun_entity_pairs), 4)

    def consistency(self, answer_a: str, answer_b: str) -> float:
        """BoW cosine similarity between two strings (no API)."""
        return _bow_cosine(answer_a, answer_b)

    def topic_tracking(self, conv: Conversation, expected_topics: list[str]) -> float:
        """Fraction of assistant turns that contain a word from the expected topic."""
        assistant_turns = conv.get_assistant_turns()
        if not expected_topics or not assistant_turns:
            return 0.0
        pairs = list(zip(assistant_turns, expected_topics, strict=False))
        correct = 0
        for turn, topic in pairs:
            topic_words = set(w.lower() for w in topic.split())
            turn_lower = turn.lower()
            if any(word in turn_lower for word in topic_words):
                correct += 1
        return round(correct / len(pairs), 4)

    def memory_window_used(self, conv: Conversation, fact: str) -> int:
        """Distance (in turns from the end) of the oldest assistant turn containing fact."""
        assistant_turns = conv.get_assistant_turns()
        fact_lower = fact.lower()
        for i, turn in enumerate(reversed(assistant_turns)):
            if fact_lower in turn.lower():
                return i + 1
        return 0

    def context_overflow_detected(self, conv: Conversation) -> bool:
        """True if the conversation exceeds the memory window."""
        return conv.num_turns() > self._memory_window

    def conversation_summarization_score(self, summary: str, conv: Conversation) -> float:
        """BoW overlap between summary and the full conversation content."""
        all_content = " ".join(m.content for m in conv.messages)
        return _bow_cosine(summary, all_content)

    def evaluate(
        self,
        conv: Conversation,
        key_facts: list[str],
        pronoun_entity_pairs: list[tuple[str, str]],
        expected_topics: list[str],
        summary: str,
    ) -> MultiTurnReport:
        """Run all metrics and return a MultiTurnReport."""
        cr = self.context_retention(conv, key_facts)
        coref = self.coreference_resolution(conv, pronoun_entity_pairs)
        first_turns = conv.get_assistant_turns()
        cons = self.consistency(first_turns[0], first_turns[-1]) if len(first_turns) >= 2 else 1.0
        tt = self.topic_tracking(conv, expected_topics)
        mw = self.memory_window_used(conv, key_facts[0]) if key_facts else 0
        overflow = self.context_overflow_detected(conv)
        summ = self.conversation_summarization_score(summary, conv)
        continuous = [cr, coref, cons, tt, summ]
        passed = all(v >= self._threshold for v in continuous)
        return MultiTurnReport(
            context_retention=cr,
            coreference_resolution=coref,
            consistency=cons,
            topic_tracking=tt,
            memory_window_used=mw,
            context_overflow_detected=overflow,
            conversation_summarization_score=summ,
            passed=passed,
        )
