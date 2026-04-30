# Módulo 14 — Embedding Eval

**Status:** implemented ✅

## Qué aprenderás

- Medir similitud semántica con embeddings coseno sin llamadas a APIs
- Detectar regresión semántica con `EmbeddingRegressionChecker`
- Calcular métricas de recuperación de información: NDCG@k, MRR@k, MAP@k
- Monitorizar drift de embeddings con centroid shift

## Capítulo del manual

Cubre la sección 16.3 del manual (`docs/` → métricas de recuperación de información) y la sección 8.1 (similitud semántica con embeddings para evaluación determinística).

## Cómo ejecutar

```bash
cd modules/14-embedding-eval
uv sync --extra embeddings
pytest tests/ -v -m "not slow"
```

## Requisitos

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) instalado
- Sin API key: todos los tests usan `MockEmbeddingModel` con hashlib determinista

## Nota especial sobre imports

Este módulo inserta `src/` directamente en `sys.path` (en lugar del directorio raíz del módulo) para evitar colisión con el namespace `src`. Los imports en tests son directos:

```python
from embedding_evaluator import EmbeddingRegressionChecker
from retrieval_metrics import ndcg_at_k, evaluate_retrieval
```
