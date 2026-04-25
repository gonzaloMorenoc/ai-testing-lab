"""Response generator: template fallback or Groq when GROQ_API_KEY is set."""

from __future__ import annotations

import os

from retriever import Document


def generate(query: str, context: list[Document]) -> str:
    """Return a grounded answer for *query* using *context* documents."""
    if not context:
        return "I don't have enough information to answer that question."

    context_text = "\n\n".join(f"[{doc.id}] {doc.content}" for doc in context)
    api_key = os.getenv("GROQ_API_KEY")

    if api_key:
        return _groq_generate(query, context_text, api_key)
    return _template_generate(query, context_text)


def _template_generate(query: str, context_text: str) -> str:
    return (
        f"Based on the available information:\n\n"
        f"{context_text}\n\n"
        f"Answer: The answer to '{query}' can be found in the context above."
    )


def _groq_generate(query: str, context_text: str, api_key: str) -> str:
    try:
        import httpx

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant. Answer the question using only the provided context. "
                        "If the context does not contain enough information, say so."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context_text}\n\nQuestion: {query}",
                },
            ],
            "max_tokens": 512,
            "temperature": 0.1,
        }
        resp = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        return _template_generate(query, context_text) + f"\n\n[Groq unavailable: {exc}]"
