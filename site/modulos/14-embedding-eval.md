# 14 — embedding-eval

**Concepto:** Evaluar similitud semántica con embeddings. Regresión semántica y detección de drift a nivel de corpus.

**Tests:** 15 · **Tiempo:** ~0.06s · **API key:** no necesaria

## Qué aprenderás

- `MockEmbeddingModel`: embeddings deterministas con hashlib para tests sin API
- `SemanticSimilarityMetric`: similitud coseno entre expected y actual output
- `EmbeddingRegressionChecker`: detectar si el candidato se aleja semánticamente del baseline
- `compute_centroid_shift`: medir drift semántico a nivel de corpus completo

## Ejecutar

```bash
pytest modules/14-embedding-eval/tests/ -m "not slow" -q
```

## Código de ejemplo

```python
from src.embedding_evaluator import MockEmbeddingModel, SemanticSimilarityMetric, EmbeddingRegressionChecker
from src.semantic_drift import compute_centroid_shift, semantic_drift_alert

model = MockEmbeddingModel(dim=64)
metric = SemanticSimilarityMetric(model, threshold=0.7)

# Comparar respuesta esperada vs real
result = metric.measure(
    expected="El envío tarda entre 3 y 5 días laborables.",
    actual="Los pedidos se entregan en 3-5 días hábiles.",
)
print(result.similarity)  # ~0.85 (semánticamente similar)
print(result.passed)      # True

# Drift de corpus completo
shift = compute_centroid_shift(corpus_referencia, corpus_actual, model)
print(f"Centroid shift: {shift:.4f}")  # < 0.1 = sin drift significativo

# Alerta automática
alert = semantic_drift_alert(model, threshold=0.1)
drift_result = alert(corpus_referencia, corpus_actual)
if drift_result.triggered:
    print(f"ALERTA: {drift_result.message}")
```

## Por qué importa

Las métricas de overlap léxico (RAGAS, groundedness) no detectan paráfrasis. Si el modelo empieza a responder con sinónimos distintos a los del baseline, el drift semántico lo detecta aunque las palabras sean diferentes.
