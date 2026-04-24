from __future__ import annotations

KNOWLEDGE_BASE: dict[str, str] = {
    "returns": (
        "Our return policy allows customers to return any product within 30 days "
        "of purchase for a full refund. Items must be in their original condition "
        "and packaging. Digital products are non-refundable once downloaded."
    ),
    "shipping": (
        "We offer free standard shipping on orders over $50. "
        "Standard shipping takes 3-5 business days. "
        "Express shipping (1-2 days) is available for $9.99."
    ),
    "warranty": (
        "All products come with a 1-year manufacturer warranty. "
        "Extended warranties of 2 or 3 years are available at purchase. "
        "Warranty covers manufacturing defects but not accidental damage."
    ),
    "payment": (
        "We accept Visa, Mastercard, American Express, PayPal, and bank transfers. "
        "All payments are processed securely via SSL encryption. "
        "We do not store credit card information."
    ),
}

TOPIC_KEYWORDS: dict[str, list[str]] = {
    "returns": ["return", "refund", "devol", "reembolso", "back"],
    "shipping": ["ship", "deliver", "envío", "envio", "days", "express"],
    "warranty": ["warrant", "garantía", "garantia", "defect", "repair"],
    "payment": ["pay", "card", "credit", "visa", "mastercard", "paypal"],
}


class RAGPipeline:
    def retrieve(self, query: str, k: int = 2) -> list[str]:
        query_lower = query.lower()
        scored: list[tuple[int, str]] = []
        for topic, keywords in TOPIC_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > 0:
                scored.append((score, KNOWLEDGE_BASE[topic]))
        scored.sort(key=lambda x: x[0], reverse=True)
        chunks = [chunk for _, chunk in scored[:k]]
        return chunks if chunks else [list(KNOWLEDGE_BASE.values())[0]]

    def generate(self, query: str, context: list[str]) -> str:
        combined = " ".join(context)
        return f"Based on our policies: {combined}"

    def run(self, query: str) -> dict[str, object]:
        context = self.retrieve(query)
        response = self.generate(query, context)
        return {"query": query, "response": response, "context": context}
