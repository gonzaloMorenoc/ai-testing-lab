# Observabilidad y drift monitoring

Cómo instrumentar un pipeline LLM para detectar problemas antes de que los reporten los usuarios.

## El problema en producción

En producción, los LLMs se degradan de formas silenciosas:

- Los scores de calidad bajan gradualmente sin que haya un cambio explícito en el modelo
- El retriever empieza a devolver chunks menos relevantes porque los datos han cambiado
- El modelo de base fue actualizado por el proveedor sin aviso
- La distribución de preguntas de los usuarios ha cambiado

Sin observabilidad, esto se detecta cuando los usuarios se quejan. Con las herramientas de los módulos 12, 13 y 14, lo detectas antes.

## Capa 1: Trazas (módulo 12)

OpenTelemetry permite instrumentar cada etapa del pipeline con spans:

```python
from src.tracer import trace

@trace("retrieval")
def retrieve(query: str) -> list[str]: ...

@trace("reranking")
def rerank(chunks: list[str]) -> list[str]: ...

@trace("generation")
def generate(query: str, context: list[str]) -> str: ...
```

Cada span registra: duración, tokens usados, errores. Se visualiza en Langfuse o Phoenix.

## Capa 2: Alertas de score (módulo 13)

Comparar los scores actuales con una distribución de referencia:

```python
from src.drift_detector import compute_psi
from src.alert_rules import mean_drop_alert, psi_alert, evaluate_rules

rules = [
    mean_drop_alert(reference_mean=0.85, threshold_pct=0.10),
    psi_alert(threshold=0.20),
]
results = evaluate_rules(rules, scores_semana_actual)
```

## Capa 3: Drift semántico (módulo 14)

El PSI mide cambios en la distribución de scores numéricos. El centroid shift mide si el significado de las respuestas ha cambiado:

```python
from src.semantic_drift import compute_centroid_shift, semantic_drift_alert

shift = compute_centroid_shift(corpus_referencia, corpus_actual, model)
# < 0.1: sin cambio
# > 0.1: las respuestas se están alejando semánticamente del baseline
```

## Pipeline de monitorización recomendado

```
Cada día:
  1. Calcular scores (faithfulness, answer_relevancy) sobre muestra aleatoria
  2. Ejecutar alert rules → registrar en AlertHistory
  3. Calcular centroid shift del corpus del día
  4. Si hay alertas → notificar al equipo

Cada semana:
  1. Revisar tendencias (degrading / recovering / stable)
  2. Actualizar corpus de referencia si la distribución de preguntas ha cambiado
```
