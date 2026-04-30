---
title: "03 — llm-as-judge"
---

# 03 — llm-as-judge

Usar un LLM como juez con G-Eval y DAG Metric. Detectar y mitigar position bias.

<div class="module-layout">
<div class="module-main">

## El problema

Tienes dos versiones de un modelo y quieres saber cuál responde mejor. Usas un LLM como juez para comparar las respuestas. El problema: el juez puntúa más alto la respuesta que aparece primero, independientemente de su calidad. Este sesgo de posición invalida completamente los resultados si no se controla. Un sistema de evaluación con LLM-as-judge no calibrado es peor que la revisión manual: da una falsa sensación de objetividad.

## Cómo funciona

Hay dos enfoques complementarios para evaluar con LLM-as-judge:

- **G-Eval**: el juez recibe una rúbrica y puntúa de 0 a 1. Flexible, pero el output depende del orden de los inputs.
- **Position bias**: en comparaciones A/B, si A aparece antes, el juez tiende a preferirla. Se mide evaluando en ambos órdenes (A→B y B→A) y calculando el delta.
- **Calibración**: evaluar los dos órdenes y promediar elimina el sesgo sistemático.
- **DAG Metric**: alternativa sin LLM. Define la evaluación como grafo de condiciones booleanas (AND, OR). Determinista y reproducible.

```text
respuesta A + respuesta B → juez (orden 1) → score_AB
respuesta B + respuesta A → juez (orden 2) → score_BA
                                 ↓
                promedio → calibrated_winner
```

## Código paso a paso

**Paso 1 — Crear `GEvalJudge` y puntuar con criterios personalizados**

```python
from src.geval_judge import GEvalJudge

judge = GEvalJudge()

result = judge.evaluate(
    output="Puedes devolver el producto en 30 días según la política de devoluciones.",
    criteria="faithfulness",
    threshold=0.7,
)
print(result.score)   # 0.0 – 1.0
print(result.passed)  # True si score >= threshold
print(result.reason)  # explicación textual
```

**Paso 2 — Calibrar position bias con dos respuestas**

```python
result = judge.calibrate_for_position_bias(
    output_a="Respuesta A: política clara de 30 días para devoluciones.",
    output_b="Respuesta B: no hay información sobre devoluciones.",
    criteria="relevancy",
)
```

**Paso 3 — Interpretar `bias_delta` y `calibrated_winner`**

```python
print(result["bias_delta"])        # delta entre orden A→B y B→A
print(result["bias_detected"])     # True si bias_delta > 0.05
print(result["calibrated_winner"]) # "A", "B" o "tie"
print(result["calibrated_score_a"])
print(result["calibrated_score_b"])

# Un bias_delta alto significa que el juez es muy sensible al orden
# En ese caso, los resultados de una evaluación A/B sin calibrar no son fiables
if result["bias_detected"]:
    print("Position bias detectado: usa solo calibrated_winner")
```

## Técnicas avanzadas

Además del position bias, los jueces LLM tienen otros cuatro sesgos sistemáticos que pueden invalidar tus resultados si no los detectas. El módulo incluye herramientas para cada uno de ellos.

```python
from src.judge_bias import detect_verbosity_bias, JudgeBiasType

# Verbosity bias: el juez puntúa más alto la respuesta más larga
# aunque tenga el mismo contenido informativo
bias = detect_verbosity_bias(
    score_short=0.60,
    score_long=0.85,
    length_ratio=3.0,  # la respuesta larga es 3 veces más larga
)
print(bias.detected)   # True (length_ratio > 2.0 AND delta > 0.15)
print(bias.severity)   # 0.0 – 1.0
print(bias.evidence)   # "length_ratio=3.00, score_delta=0.250"
```

Los 5 tipos de sesgo detectados: `VERBOSITY`, `SELF_ENHANCEMENT`, `POSITION`, `LENIENT`, `FORMAT`.

Cuando múltiples evaluadores (humanos o LLMs) puntúan el mismo conjunto, necesitas medir si están de acuerdo o si sus diferencias son sistemáticas. El coeficiente kappa de Cohen cuantifica el acuerdo más allá del azar:

```python
from src.judge_bias import cohen_kappa

result = cohen_kappa(
    annotations_a=[1, 0, 1, 1, 0, 1, 0, 0, 1, 1],
    annotations_b=[1, 0, 0, 1, 0, 1, 0, 1, 1, 0],
)
print(result.score)           # κ ≈ 0.60
print(result.acceptable)      # True si score >= 0.61
print(result.interpretation)  # "sustancial" | "casi perfecto" | "moderado" | ...

# Si κ < 0.41: los evaluadores no se ponen de acuerdo;
# revisa las guidelines antes de confiar en los resultados
```

## Errores comunes

- **Comparar A/B con una sola evaluación en orden fijo** — el ganador puede ser el que aparece primero. Siempre evalúa en ambos órdenes y promedia.
- **Usar el mismo modelo como generador y juez** — el juez favorece su propio estilo. Usa modelos distintos para generación y evaluación.
- **Ignorar verbosity bias** — el juez puntúa respuestas largas por defecto. Controla longitud en el dataset o usa `detect_verbosity_bias`.
- **Un único evaluador sin medida de acuerdo** — sin confiabilidad. Calcula Cohen kappa con ≥ 2 evaluadores, umbral κ ≥ 0.61.

## En producción

| Indicador        | Umbral             |
|------------------|--------------------|
| bias_delta       | < 0.10             |
| Cohen kappa (κ)  | ≥ 0.61             |
| n_samples mínimo | 30 por comparación |

Ejecuta los tests en CI con:

```bash
pytest modules/03-llm-as-judge/tests/ -m "not slow" -q
```

Para detectar drift en los scores del juez a lo largo del tiempo, consulta el módulo 13.

## Caso real en producción

Empresa de RRHH usando un LLM para cribar CVs comparando dos versiones del modelo de scoring. En una evaluación A/B con 200 CVs, el modelo B ganaba en el 67% de los casos. Tras calibrar el position bias, el resultado fue un empate técnico (51% B, diferencia no significativa). El equipo había estado a punto de migrar a un modelo más caro basándose en un artefacto estadístico.

## Ejercicios

**🟢 Básico** — Ejecuta `calibrate_for_position_bias` con dos respuestas donde la primera es claramente peor. El archivo de test está en `modules/03-llm-as-judge/tests/test_judges.py`. Ejecuta:

```bash
pytest modules/03-llm-as-judge/tests/ -m "not slow" -q
```

¿El `calibrated_winner` cambia respecto a la evaluación sin calibrar?

**🟡 Intermedio** — Implementa un test que detecte verbosity bias: genera una respuesta corta y una larga con el mismo contenido informativo y verifica que `detect_verbosity_bias` lo identifica cuando el score de la larga supera en 0.15+ a la corta.

**🔴 Avanzado** — Diseña un benchmark de 20 pares de respuestas con Cohen kappa real entre dos "jueces". Calcula κ e interpreta si el acuerdo es aceptable según los umbrales de Landis & Koch (κ ≥ 0.61 sustancial, κ ≥ 0.81 casi perfecto).

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
