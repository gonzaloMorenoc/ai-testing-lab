---
title: "14 — embedding-eval"
---

# 14 — embedding-eval

Evaluar similitud semántica con embeddings. Regresión semántica y detección de drift a nivel de corpus.

<div class="module-layout">
<div class="module-main">

## El problema

Tu sistema de búsqueda semántica funcionaba bien. Ahora los candidatos relevantes aparecen en posición 8 o 9 en lugar de en el top-3. El modelo de embeddings no ha cambiado. ¿Qué pasó? Los datos del corpus han cambiado — el centroide semántico se ha desplazado. Sin detección de drift semántico, este tipo de degradación es invisible hasta que los usuarios se quejan.

## Cómo funciona

- **Similitud coseno:** distancia angular entre dos vectores. 1.0 = idénticos, 0.0 = ortogonales.
- **`MockEmbeddingModel`:** genera embeddings deterministas con hashlib. Sin llamadas a OpenAI — todos los tests son reproducibles.
- **`EmbeddingRegressionChecker`:** compara si el candidato se aleja semánticamente del baseline más del threshold permitido.
- **`compute_centroid_shift`:** calcula la distancia coseno entre el centroide del corpus de referencia y el corpus actual.
- **Métricas de ranking (NDCG, MRR, MAP):** miden si los documentos relevantes aparecen en las posiciones más altas.

```text
texto → MockEmbeddingModel → vector[64] → cosine_similarity(expected, actual) → score
corpus_ref + corpus_actual → compute_centroid_shift → drift_score
```

## Código paso a paso

**1. Crear `MockEmbeddingModel` y `SemanticSimilarityMetric`, medir similitud**

`MockEmbeddingModel` usa hashlib para generar embeddings deterministas: cada palabra se convierte en un vector via `md5` + semilla aleatoria. `SemanticSimilarityMetric` mide la similitud coseno entre dos textos y devuelve un `SimilarityResult` con el score y si supera el threshold.

```python
from src.embedding_evaluator import MockEmbeddingModel, SemanticSimilarityMetric

model = MockEmbeddingModel(dim=64)
metric = SemanticSimilarityMetric(model, threshold=0.7)

result = metric.measure(
    expected="El envío tarda entre 3 y 5 días laborables.",
    actual="Los pedidos se entregan en 3-5 días hábiles.",
)
print(result.similarity)  # > 0.7
print(result.passed)      # True
```

**2. Usar `EmbeddingRegressionChecker` para detectar si el candidato se aleja del baseline**

`EmbeddingRegressionChecker` compara una lista de outputs esperados contra una lista de candidatos. Devuelve un `EmbeddingRegressionReport` con `pass_rate`, `passed` y `failed`.

```python
from src.embedding_evaluator import MockEmbeddingModel, EmbeddingRegressionChecker

model = MockEmbeddingModel(dim=64)
checker = EmbeddingRegressionChecker(model, threshold=0.7)

expected_outputs = [
    "El envío tarda 3 días.",
    "El pedido llegará el viernes.",
]
candidate_outputs = [
    "Los pedidos se entregan en 72 horas.",
    "Recibirás tu paquete antes del viernes.",
]

report = checker.check(expected_outputs, candidate_outputs)
print(report.pass_rate)  # 1.0 si ambos superan 0.7
print(report.summary())
```

**3. Usar `compute_centroid_shift` con dos corpus y `semantic_drift_alert`**

`compute_centroid_shift` calcula la distancia coseno entre los centroides de dos corpus. `semantic_drift_alert` devuelve una función que compara dos corpus y dispara si el drift supera el threshold.

```python
from src.embedding_evaluator import MockEmbeddingModel
from src.semantic_drift import compute_centroid_shift, semantic_drift_alert

model = MockEmbeddingModel(dim=64)

corpus_ref = ["envío rápido", "entrega express", "paquete urgente"]
corpus_actual = ["diagnóstico médico", "historial clínico", "consulta urgencias"]

shift = compute_centroid_shift(corpus_ref, corpus_actual, model)
print(f"centroid_shift = {shift:.4f}")  # > 0.1

alert = semantic_drift_alert(model, threshold=0.1)
result = alert(corpus_ref, corpus_actual)
print(result.triggered)  # True
print(result.message)
```

## Técnicas avanzadas

La similitud coseno mide si dos respuestas son parecidas. NDCG, MRR y MAP miden si los documentos relevantes aparecen donde el usuario los espera — en las posiciones más altas del ranking. Son métricas complementarias: una mide calidad semántica de la respuesta, las otras miden calidad de ordenación del retriever.

```python
from src.retrieval_metrics import evaluate_retrieval, ndcg_at_k, mrr_at_k, map_at_k

# Evaluación sobre N queries
report = evaluate_retrieval(
    relevant_sets=[{0, 2, 4}, {1, 3}],          # docs relevantes por query
    ranked_lists=[[0, 1, 2, 3, 4], [1, 0, 3]],  # docs recuperados (ordenados)
    k=3,
    threshold=0.5,
)
print(report.ndcg, report.mrr, report.map_score, report.passed)

# Métricas individuales
ndcg = ndcg_at_k(relevant_ids={0, 1, 2}, ranked_ids=[0, 1, 2, 3], k=3)  # 1.0
mrr  = mrr_at_k(relevant_ids={2}, ranked_ids=[0, 1, 2, 3], k=3)          # 0.333
ap   = map_at_k(relevant_ids={0, 2}, ranked_ids=[0, 1, 2], k=3)          # 0.833
```

## Errores comunes

- ❌ Similitud coseno sin threshold calibrado → no sabes qué score indica "suficientemente similar". ✅ Calibrar el threshold con pares de respuestas humanas etiquetadas.
- ❌ Evaluar solo pares individuales → no detecta drift del corpus completo. ✅ Usar `compute_centroid_shift` periódicamente.
- ❌ NDCG@k sin definir k → k depende de cuántos resultados muestra la UI. ✅ Usar el mismo k que muestra la interfaz (típicamente 3, 5 o 10).
- ❌ Asumir que embeddings de OpenAI son deterministas → pueden cambiar. ✅ Usar `MockEmbeddingModel` en tests, embeddings reales en evaluación periódica.

## En producción

| Métrica           | Umbral         |
|-------------------|----------------|
| similitud coseno  | ≥ 0.70         |
| centroid_shift    | < 0.10         |
| NDCG@5            | ≥ 0.75         |
| MRR@5             | ≥ 0.70         |

```bash
# CI
pytest modules/14-embedding-eval/tests/ -m "not slow" -q
```

Para monitorizar drift semántico en el tiempo → módulo 13.

## Caso real en producción

Plataforma de empleo con búsqueda semántica de candidatos. Tras incorporar nuevas ofertas de trabajo de un sector emergente (IA generativa), el centroide del corpus de candidatos se desplazó 0.18 puntos. NDCG@5 bajó de 0.81 a 0.64 — los reclutadores tardaban el doble en encontrar candidatos relevantes. El equipo detectó el shift con `compute_centroid_shift` antes de que llegaran quejas y reindexó el corpus con el nuevo vocabulario del sector.

## Ejercicios

- 🟢 Mide la similitud coseno entre "El envío tarda 3 días" y "Los pedidos se entregan en 72 horas". Busca el archivo de test en `modules/14-embedding-eval/tests/test_embedding_eval.py` y ejecuta `pytest modules/14-embedding-eval/tests/ -m "not slow" -q`. ¿Supera 0.7?
- 🟡 Genera dos corpus de 10 documentos cada uno con un shift semántico claro (uno sobre e-commerce, otro sobre sanidad). Verifica que `compute_centroid_shift` detecta la diferencia y supera el threshold de 0.1.
- 🔴 Implementa una evaluación de retrieval completa con 5 queries, sus documentos relevantes y los rankings devueltos por tu sistema. Calcula NDCG@3, MRR@3 y MAP@3. ¿Cuál es el indicador más sensible en tu dataset?

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">33</div>
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
