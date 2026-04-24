from __future__ import annotations

from src.conversation import Conversation

KNOWLEDGE_BASE: dict[str, str] = {
    "returns": "Returns allowed within 30 days for a full refund. Original condition required.",
    "shipping": "Free shipping over $50. Standard 3-5 days. Express $9.99 for 1-2 days.",
    "warranty": "1-year manufacturer warranty. Extended 2-3 year options available.",
    "payment": "Visa, Mastercard, Amex, PayPal accepted. SSL encrypted. No stored cards.",
}

TOPIC_KEYWORDS: dict[str, list[str]] = {
    "returns": ["return", "refund", "back"],
    "shipping": ["ship", "deliver", "days", "express"],
    "warranty": ["warrant", "defect", "repair"],
    "payment": ["pay", "card", "visa", "paypal"],
}


class MultiTurnRAG:
    def __init__(self) -> None:
        self.conversation = Conversation()

    def _retrieve(self, query: str) -> list[str]:
        q = query.lower()
        chunks = []
        for topic, keywords in TOPIC_KEYWORDS.items():
            if any(kw in q for kw in keywords):
                chunks.append(KNOWLEDGE_BASE[topic])
        return chunks or [KNOWLEDGE_BASE["returns"]]

    def _build_context_summary(self) -> str:
        prior = self.conversation.get_assistant_turns()[-2:]
        return " Previously discussed: " + " ".join(prior) if prior else ""

    def respond(self, user_input: str) -> str:
        context = self._retrieve(user_input)
        history_context = self._build_context_summary()
        response = f"Based on our policies: {' '.join(context)}{history_context}"
        self.conversation.add_turn(user_input, response)
        return response

    def reset(self) -> None:
        self.conversation.reset()
