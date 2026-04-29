# 03 — llm-as-judge

**Concepto:** Usar un LLM como juez con G-Eval y DAG Metric. Detectar y mitigar position bias.

**Tests:** 11 · **Tiempo:** ~0.05s · **API key:** no necesaria

## Qué aprenderás

- Cómo funciona G-Eval: rúbrica personalizada → LLM puntúa de 0 a 1
- DAG Metric: lógica de evaluación compuesta (AND, OR) sin LLM juez
- Position bias: por qué el juez puntúa más alto la respuesta que aparece primero
- Cómo calibrar el position bias evaluando en ambos órdenes y promediando

## Ejecutar

```bash
pytest modules/03-llm-as-judge/tests/ -m "not slow" -q
```

## Código de ejemplo

```python
from src.geval_judge import GEvalJudge

judge = GEvalJudge()

# Calibración de position bias
result = judge.calibrate_for_position_bias(
    output_a="Respuesta A del modelo",
    output_b="Respuesta B del modelo",
    criteria="relevancia y precisión factual",
)
print(result["bias_delta"])        # diferencia entre orden A→B y B→A
print(result["calibrated_winner"]) # "A", "B" o "tie"
```

## Por qué importa

Sin calibración, el 60-70% de las comparaciones A/B con LLM-as-judge están sesgadas hacia la posición. Esto invalida completamente los resultados de evaluación comparativa.
