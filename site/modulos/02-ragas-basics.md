# 02 — ragas-basics

**Concepto:** Evaluar un pipeline RAG completo con las métricas de RAGAS.

**Tests:** 10 · **Tiempo:** ~0.05s · **API key:** no necesaria

## Qué aprenderás

- Las tres métricas core de RAGAS: faithfulness, context precision y answer relevancy
- Cómo construir un `RAGASEvaluator` reutilizable
- La diferencia entre evaluar el retriever (context precision) y el generador (faithfulness)
- Cómo inyectar clusters de sinónimos de dominio para mejorar la precisión

## Ejecutar

```bash
pytest modules/02-ragas-basics/tests/ -m "not slow" -q
```

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

Context precision y context recall miden cosas distintas: un retriever puede devolver muchos chunks relevantes (alto recall) pero también muchos irrelevantes (baja precision). RAGAS te permite medir ambos por separado para diagnosticar dónde está el problema.
