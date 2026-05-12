"""Precios por 1000 tokens, externalizados a configuración.

Manual QA AI v13 §27.3 (nota técnica): "Nunca hardcodear precios en código de
producción; los proveedores cambian con frecuencia. Externalizar a config o
secret manager."

Este módulo expone un diccionario por defecto (precios fecha 2026-04) y una
función para cargar overrides desde un JSON. En proyectos reales, sustituir
por una fuente firmada (Vault, AWS Secrets Manager, etc.).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TokenPrice:
    """Precio por 1 000 tokens de un modelo."""

    in_per_1k_usd: float
    out_per_1k_usd: float


# TODO: leer de config / secret manager. Precios fecha 2026-04. Verificar
# siempre en la doc oficial del proveedor antes de usar en producción.
PRICE_PER_1K: dict[str, TokenPrice] = {
    "gpt-4o": TokenPrice(0.0025, 0.010),
    "gpt-4o-mini": TokenPrice(0.00015, 0.0006),
    "claude-sonnet-4-5": TokenPrice(0.003, 0.015),
    "claude-haiku-4-5": TokenPrice(0.0008, 0.004),
    "groq/llama-3.3-70b": TokenPrice(0.00059, 0.00079),
}


def load_prices_from_config(path: Path | None = None) -> dict[str, TokenPrice]:
    """Carga precios desde un JSON externo, con fallback al default.

    Formato del JSON esperado:
        {"<model_id>": {"in_per_1k_usd": 0.0025, "out_per_1k_usd": 0.010}, ...}

    Si path es None, devuelve el diccionario por defecto. Si path no existe,
    eleva FileNotFoundError (fallo explícito, nunca silente).
    """
    if path is None:
        return dict(PRICE_PER_1K)
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"price config no encontrado: {p}")
    raw = json.loads(p.read_text(encoding="utf-8"))
    return {
        model: TokenPrice(float(v["in_per_1k_usd"]), float(v["out_per_1k_usd"]))
        for model, v in raw.items()
    }
