"""
RAG mínimo para el módulo 01. Knowledge base hardcodeada, sin dependencias externas.
Sirve como sistema bajo prueba (SUT) para los tests de evaluación.
"""

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
    "returns": ["return", "refund", "devol", "devoluc", "reembolso"],
    "shipping": ["ship", "delivery", "envío", "envio", "entrega"],
    "warranty": ["warranty", "garantía", "garantia", "defect"],
    "payment": ["pay", "payment", "pago", "credit", "card"],
}


class SimpleRAG:
    """
    RAG mínimo para demostración. Retrieval por coincidencia de palabras clave.
    No usar en producción.
    """

    def retrieve(self, query: str) -> list[str]:
        query_lower = query.lower()
        matched: list[str] = []
        for topic, keywords in TOPIC_KEYWORDS.items():
            if any(kw in query_lower for kw in keywords):
                matched.append(KNOWLEDGE_BASE[topic])
        return matched if matched else [KNOWLEDGE_BASE["returns"]]

    def generate(self, query: str, context: list[str]) -> str:
        combined = " ".join(context)
        return f"Based on our policies: {combined}"

    def query(self, user_input: str) -> tuple[str, list[str]]:
        """Devuelve (respuesta, lista_de_chunks_de_contexto)."""
        context = self.retrieve(user_input)
        response = self.generate(user_input, context)
        return response, context
