"""FastAPI entry point for the simple-rag demo."""

from __future__ import annotations

from fastapi import FastAPI
from generator import generate
from pydantic import BaseModel
from retriever import Document, InMemoryKB

app = FastAPI(title="Simple RAG Demo", version="0.1.0")

_SEED_DOCS = [
    Document(
        id="rag-001",
        content=(
            "RAG (Retrieval-Augmented Generation) is a hybrid AI architecture that retrieves "
            "relevant documents from a knowledge base and provides them as context to a language model."
        ),
        metadata={"domain": "ai_fundamentals"},
    ),
    Document(
        id="rag-002",
        content=(
            "Faithfulness is a RAG evaluation metric that checks whether the generated response "
            "is grounded in the provided context chunks. A faithful response contains no unsupported claims."
        ),
        metadata={"domain": "rag_metrics"},
    ),
    Document(
        id="rag-003",
        content=(
            "Context precision measures the signal-to-noise ratio of retrieved chunks. "
            "High precision means most retrieved chunks are relevant to the question."
        ),
        metadata={"domain": "rag_metrics"},
    ),
    Document(
        id="rag-004",
        content=(
            "Context recall checks whether the retrieved documents cover all facts needed "
            "to answer the question completely."
        ),
        metadata={"domain": "rag_metrics"},
    ),
    Document(
        id="rag-005",
        content=(
            "Hallucination in LLMs refers to generating confident but factually incorrect "
            "or unsupported information. RAG reduces hallucinations by grounding responses in retrieved evidence."
        ),
        metadata={"domain": "llm_safety"},
    ),
]

_kb = InMemoryKB(_SEED_DOCS)


class QueryRequest(BaseModel):
    question: str
    top_k: int = 3


class QueryResponse(BaseModel):
    question: str
    answer: str
    context: list[dict]


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "documents": len(_SEED_DOCS)}


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest) -> QueryResponse:
    docs = _kb.retrieve(req.question, top_k=req.top_k)
    answer = generate(req.question, docs)
    return QueryResponse(
        question=req.question,
        answer=answer,
        context=[{"id": d.id, "content": d.content} for d in docs],
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
