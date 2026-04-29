---
title: "14 — embedding-eval"
---

# 14 — embedding-eval

Evaluar similitud semántica con embeddings. Regresión semántica y detección de drift a nivel de corpus.

<div class="module-layout">
<div class="module-main">

## Qué aprenderás

- `MockEmbeddingModel`: embeddings deterministas con hashlib para tests sin API
- `SemanticSimilarityMetric`: similitud coseno entre expected y actual output
- `EmbeddingRegressionChecker`: detectar si el candidato se aleja semánticamente del baseline
- `compute_centroid_shift`: medir drift semántico a nivel de corpus completo

## Código de ejemplo

```python
from src.embedding_evaluator import MockEmbeddingModel, SemanticSimilarityMetric
from src.semantic_drift import compute_centroid_shift, semantic_drift_alert

model = MockEmbeddingModel(dim=64)
metric = SemanticSimilarityMetric(model, threshold=0.7)

result = metric.measure(
    expected="El envío tarda entre 3 y 5 días laborables.",
    actual="Los pedidos se entregan en 3-5 días hábiles.",
)
print(result.similarity)  # ~0.85
print(result.passed)      # True

# Drift de corpus completo
shift = compute_centroid_shift(corpus_referencia, corpus_actual, model)
alert = semantic_drift_alert(model, threshold=0.1)
drift_result = alert(corpus_referencia, corpus_actual)
```

## Por qué importa

> Las métricas de overlap léxico no detectan paráfrasis. Si el modelo empieza a responder con sinónimos distintos a los del baseline, el drift semántico lo detecta aunque las palabras sean diferentes.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">15</div>
  <div class="stat-label">tests</div>
</div>

<div class="stat-card">
  <div class="stat-number">0.06s</div>
  <div class="stat-label">duración</div>
</div>

<div class="stat-card stat-ok">
  <div class="stat-number">✓</div>
  <div class="stat-label">sin API key</div>
</div>

<div class="stat-card">
  <div class="stat-number level">Avanzado</div>
  <div class="stat-label">nivel</div>
</div>

```bash
pytest modules/14-embedding-eval/tests/ \
  -m "not slow" -q
```

<div class="module-next">
  <div class="next-label">Fin del lab</div>
  <a href="/modulos/">← Ver todos</a>
</div>

</div>
</div>
