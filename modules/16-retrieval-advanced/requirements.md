# Requisitos del módulo 16

## Dependencias

Solo stdlib. `ranx` es opcional: si está instalado, los proyectos pueden
sustituir las métricas internas (`ndcg_at_k`, `mrr_at_k`, `map_at_k`) por las
de `ranx` sin cambiar la API.

## Variables de entorno

Ninguna.

## Markers pytest

- `not slow` (por defecto).

## Cómo extenderlo

- Para añadir una técnica: implementar la interfaz `retrieve(query, top_k) -> list[Document]`
  y `cost_overhead() -> dict[str, float]`. Añadir entrada en `trade_offs.py`.
- Para usar embeddings reales: sustituir `_dense_score` por un encoder real
  (sentence-transformers). El resto del pipeline no cambia.
