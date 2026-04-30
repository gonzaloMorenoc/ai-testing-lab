---
title: "02 — ragas-basics"
---

# 02 — ragas-basics

Evaluar un pipeline RAG completo: diagnostica retriever y generador por separado con tres métricas.

<div class="module-layout">
<div class="module-main">

## El problema

Tu pipeline RAG devuelve respuestas, pero no sabes si el problema está en el retriever (trae chunks irrelevantes) o en el generador (no usa bien el contexto). Sin separar ambas evaluaciones, cualquier mejora es a ciegas. RAGAS te da tres métricas que diagnostican cada componente por separado: cuánto de lo que recuperaste era relevante, cuánto de lo necesario recuperaste, y si la respuesta refleja fielmente el contexto.

## Cómo funciona

`context_precision`, `context_recall` y `faithfulness` miden componentes distintos del pipeline:

- **`context_precision`**: de los chunks recuperados, ¿qué fracción era necesaria? Mide el retriever. Alta precision = pocos chunks irrelevantes.
- **`context_recall`**: de la información necesaria, ¿qué fracción estaba en los chunks? Mide si el retriever no se dejó nada.
- **`faithfulness`**: ¿la respuesta generada puede inferirse del contexto? Mide el generador. Es independiente del retriever.

El `RAGASEvaluator` del lab usa word overlap en modo determinista — sin llamadas a OpenAI.

```text
query → retriever → [chunks] → generador → respuesta
                       ↓                      ↓
               context_precision        faithfulness
               context_recall
```

## Código paso a paso

**Paso 1 — Construir clusters de sinónimos de dominio**

```python
from src.ragas_evaluator import build_synonym_clusters

clusters = build_synonym_clusters(
    custom_clusters=[["devolución", "reembolso", "retorno"]],
)
# clusters es una lista de frozensets que el evaluador usa
# para expandir tokens durante el cálculo de context_precision
```

**Paso 2 — Crear el evaluador y evaluar**

```python
from src.ragas_evaluator import RAGASEvaluator

evaluator = RAGASEvaluator(synonym_clusters=clusters)

scores = evaluator.evaluate(
    query="¿Puedo devolver el producto?",
    context=[
        "Aceptamos reembolsos en 30 días.",
        "El envío estándar tarda 3-5 días hábiles.",
    ],
    response="Sí, puedes solicitar un reembolso en 30 días.",
)
```

**Paso 3 — Inspeccionar las tres métricas e interpretar qué componente falla**

```python
print(scores.faithfulness)       # ¿el generador usó el contexto?
print(scores.context_precision)  # ¿el retriever trajo chunks relevantes?
print(scores.context_recall)     # ¿el retriever se dejó información?

# Si context_precision es bajo y faithfulness es alto:
# → el problema está en el índice vectorial, no en el LLM
if scores.context_precision < 0.65:
    print("Retriever deficiente: reduce el número de chunks o añade re-ranking")

# passes() comprueba que los 4 scores superen el umbral (0.7 por defecto)
assert scores.passes(threshold=0.7)
```

## Técnicas avanzadas

En dominios con vocabulario técnico, el overlap léxico subestima la relevancia porque los sinónimos no coinciden literalmente. Los clusters de sinónimos permiten inyectar ese conocimiento de dominio sin modificar el algoritmo base.

```python
from src.ragas_evaluator import build_synonym_clusters, RAGASEvaluator

# Dominio jurídico: términos que el retriever debe tratar como equivalentes
legal_clusters = build_synonym_clusters(
    custom_clusters=[
        ["resolución", "sentencia", "fallo"],
        ["contrato", "acuerdo", "convenio"],
        ["demandante", "actor", "recurrente"],
    ],
    include_defaults=False,  # excluir clusters de e-commerce
)

evaluator = RAGASEvaluator(synonym_clusters=legal_clusters)

scores = evaluator.evaluate(
    query="¿La sentencia es apelable?",
    context=["La resolución puede recurrirse en 10 días hábiles."],
    response="Sí, el fallo admite recurso en 10 días.",
)
# context_precision reconoce 'resolución' como sinónimo de 'sentencia'
# y puntúa el chunk como relevante aunque no coincida la palabra exacta
```

## Errores comunes

- **Evaluar solo `faithfulness`** — no detectas si el retriever trae basura. Evalúa las tres métricas siempre.
- **Confundir precision con recall** — alta precision + bajo recall significa retriever conservador que se deja información crítica. Revisa ambas antes de concluir.
- **Un solo chunk en el contexto** — no ejercita el retriever. Usa al menos 3-5 chunks por query de test.
- **Queries de test demasiado simples** — no estresan el pipeline. Incluye queries con sinónimos, negaciones y preguntas ambiguas.

## En producción

| Métrica           | Mínimo | Target | Alto riesgo |
|-------------------|--------|--------|-------------|
| context_precision | 0.65   | 0.80   | 0.90        |
| context_recall    | 0.70   | 0.85   | 0.90        |
| faithfulness      | 0.70   | 0.85   | 0.90        |

Ejecuta los tests en CI con:

```bash
pytest modules/02-ragas-basics/tests/ -m "not slow" -q
```

Para detectar drift en estas métricas a lo largo del tiempo, consulta el módulo 13.

## Caso real en producción

Despacho de abogados con asistente de revisión de contratos. El retriever devolvía 5 chunks por query, pero `context_precision` era 0.41 — menos de la mitad del contexto recuperado era relevante. El generador tenía `faithfulness` de 0.89, lo que indicaba que el problema no estaba en el LLM sino en el índice vectorial. El equipo redujo el número de chunks de 5 a 3 con re-ranking y `context_precision` subió a 0.78 sin cambiar el modelo.

## Ejercicios

**🟢 Básico** — Modifica el `overlap_threshold` del evaluador a 0.3. El archivo de test principal está en `modules/02-ragas-basics/tests/test_ragas_metrics.py`. Ejecuta:

```bash
pytest modules/02-ragas-basics/tests/ -m "not slow" -q
```

¿Cómo cambian los scores de `context_precision` y `context_recall`?

**🟡 Intermedio** — Añade un caso donde el contexto tiene la información correcta pero la respuesta la ignora completamente. Verifica que `faithfulness` baja mientras `context_recall` se mantiene alto.

**🔴 Avanzado** — Construye un dataset de 10 queries con sus contextos y respuestas que simule un pipeline con retriever deficiente (baja precision) pero generador fiel. Mide las tres métricas y genera un informe que identifique el componente problemático.

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
