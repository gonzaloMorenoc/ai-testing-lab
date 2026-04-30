---
title: "03 — llm-as-judge"
---

# 03 — llm-as-judge

Usar un LLM como juez con G-Eval y DAG Metric. Detectar y mitigar position bias.

<div class="module-layout">
<div class="module-main">

## Qué aprenderás

- Cómo funciona G-Eval: rúbrica personalizada → LLM puntúa de 0 a 1
- DAG Metric: lógica de evaluación compuesta (AND, OR) sin LLM juez
- Position bias: por qué el juez puntúa más alto la respuesta que aparece primero
- Cómo calibrar el position bias evaluando en ambos órdenes y promediando

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

> Sin calibración, el 60-70% de las comparaciones A/B con LLM-as-judge están sesgadas hacia la posición. Esto invalida completamente los resultados de evaluación comparativa.

## Nuevas implementaciones (Manual QA AI v12)

**`JudgeBias`** — detección de los 5 sesgos del juez (Cap 05) y acuerdo inter-anotador IAA (Cap 28):

```python
from src.judge_bias import detect_verbosity_bias, detect_position_bias, cohen_kappa

# Sesgo de verbosidad: respuesta más larga puntuada más alto injustamente
bias = detect_verbosity_bias(score_short=0.6, score_long=0.85, length_ratio=3.0)
# bias.detected = True (ratio > 2.0 AND delta > 0.15)

# Acuerdo inter-anotador (κ Cohen)
result = cohen_kappa(
    annotations_a=[1, 0, 1, 1, 0],
    annotations_b=[1, 0, 0, 1, 0],
)
# result.score ≈ 0.60
# result.acceptable = (score >= 0.61)  → Landis & Koch
# result.interpretation = "Substantial" | "Almost perfect" | ...
```

Los 5 tipos de sesgo detectados: `VERBOSITY`, `SELF_ENHANCEMENT`, `POSITION`, `LENIENT`, `FORMAT`.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">36</div>
  <div class="stat-label">tests</div>
</div>

<div class="stat-card">
  <div class="stat-number">0.07s</div>
  <div class="stat-label">duración</div>
</div>

<div class="stat-card stat-ok">
  <div class="stat-number">✓</div>
  <div class="stat-label">sin API key</div>
</div>

<div class="stat-card">
  <div class="stat-number level">Intermedio</div>
  <div class="stat-label">nivel</div>
</div>

```bash
pytest modules/03-llm-as-judge/tests/ \
  -m "not slow" -q
```

<div class="module-next">
  <div class="next-label">Siguiente →</div>
  <a href="/modulos/14-embedding-eval">14 — embedding-eval</a>
</div>

</div>
</div>
