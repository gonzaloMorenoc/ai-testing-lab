---
title: "02 — ragas-basics"
---

# 02 — ragas-basics

Evaluar un pipeline RAG completo con las métricas core de RAGAS.

<div class="module-layout">
<div class="module-main">

## Qué aprenderás

- Las tres métricas core de RAGAS: faithfulness, context precision y answer relevancy
- Cómo construir un `RAGASEvaluator` reutilizable
- La diferencia entre evaluar el retriever (context precision) y el generador (faithfulness)
- Cómo inyectar clusters de sinónimos de dominio para mejorar la precisión

## Código de ejemplo

```python
from src.ragas_evaluator import RAGASEvaluator, build_synonym_clusters

clusters = build_synonym_clusters(
    custom_clusters=[["devolución", "reembolso", "retorno"]],
)
evaluator = RAGASEvaluator(synonym_clusters=clusters)

result = evaluator.evaluate(
    query="¿Puedo devolver el producto?",
    context=["Aceptamos reembolsos en 30 días."],
    response="Sí, puedes solicitar un reembolso en 30 días.",
)
assert result["faithfulness"] > 0.8
assert result["answer_relevancy"] > 0.7
```

## Por qué importa

> Context precision y context recall miden cosas distintas: un retriever puede devolver muchos chunks relevantes (alto recall) pero también muchos irrelevantes (baja precision). RAGAS te permite diagnosticar exactamente cuál es el problema.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">11</div>
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
  <div class="stat-number level">Básico</div>
  <div class="stat-label">nivel</div>
</div>

```bash
pytest modules/02-ragas-basics/tests/ \
  -m "not slow" -q
```

<div class="module-next">
  <div class="next-label">Siguiente →</div>
  <a href="/modulos/03-llm-as-judge">03 — llm-as-judge</a>
</div>

</div>
</div>
