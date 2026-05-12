"""Contexto del producto del caso D.1: chatbot interno para asesores de una
aseguradora médica.

Fuente: Manual QA AI v13, Apéndice D §D.1.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProductContext:
    """Contexto operacional del sistema bajo evaluación."""

    name: str = "ChatbotSaludAsesor"
    users: int = 800
    countries: tuple[str, ...] = ("ES", "PT", "EN")
    queries_per_day: int = 25_000
    peak_factor: float = 4.0  # picos de tráfico en horario comercial
    primary_llm: str = "claude-sonnet-4-5"
    classifier_llm: str = "claude-haiku-4-5"
    reranker: str = "cross-encoder-multilingual"
    corpus_docs: int = 12_000

    team_roles: tuple[str, ...] = (
        "TechLead",
        "Backend1",
        "Backend2",
        "MLEngineer",
        "QAEngineer",
        "DomainExpertLegal",
        "DomainExpertClinical",
        "SecurityLead",
    )

    def peak_queries_per_hour(self) -> int:
        """Estimación pico = (queries_day / 24h) × peak_factor."""
        per_hour = self.queries_per_day / 24
        return int(per_hour * self.peak_factor)


# Pre-construido para usar directo
DEFAULT_PRODUCT = ProductContext()
