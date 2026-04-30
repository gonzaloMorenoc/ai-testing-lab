---
title: "01 — primer-eval"
---

# 01 — primer-eval
Tu primer `LLMTestCase` con DeepEval: métricas AnswerRelevancy y Faithfulness con mocks deterministas.

<div class="module-layout">
<div class="module-main">

## El problema

Cambias el prompt de tu chatbot y las respuestas parecen mejores. ¿Pero lo son realmente? Sin métricas objetivas, la única forma de saberlo es la revisión manual — viable con 20 queries al día, imposible con 2.000. Cuando el volumen crece, necesitas un mecanismo que tome esa decisión por ti, en cada commit, sin intervención humana.

`LLMTestCase` es la unidad mínima para automatizar esa decisión: encapsula la entrada del usuario, la respuesta del modelo y el contexto recuperado del sistema RAG. Una métrica objetiva determina si la respuesta es relevante y fiel a ese contexto, sin que nadie tenga que leerla. El resultado es un valor numérico comparable con un umbral, exactamente como cualquier otro test de software. Si cae por debajo, el pipeline falla; si lo supera, el cambio puede avanzar. Así de sencillo es el salto de la evaluación subjetiva a la evaluación automatizada en CI.

## Cómo funciona

`AnswerRelevancyMetric` en modo mock calcula el solapamiento léxico normalizado entre las palabras de la query y las palabras de la respuesta. No invoca ningún LLM externo: compara vocabulario directamente, lo que hace los tests deterministas y rápidos. Un score de 1.0 significa solapamiento total; 0.0 significa que no comparten ningún término relevante.

`FaithfulnessMetric` verifica si cada afirmación de la respuesta puede inferirse del `retrieval_context`. En mock, usa overlap léxico entre los claims extraídos de la respuesta y el texto del contexto. Si la respuesta introduce información que no aparece en el contexto, el score baja.

El flujo completo es:

```text
input + actual_output + retrieval_context
          │
          ▼
     LLMTestCase
          │
          ▼
  metric.measure(test_case)
          │
          ▼
        score  ──────────────────────────┐
          │                              │
     ≥ threshold?                        │
       /       \                         │
     YES        NO                       │
      │          │                       │
    PASS        FAIL  ◄──────────────────┘
```

Ambas métricas son independientes: puedes aplicarlas por separado o combinarlas en un único `assert_test`. El threshold define el contrato de calidad del sistema.

## Código paso a paso

**Paso 1: construir el LLMTestCase**

El test case es el contenedor inmutable de los datos de una evaluación. Requiere al menos `input` (la query del usuario), `actual_output` (la respuesta del modelo) y `retrieval_context` (los fragmentos recuperados por el RAG).

```python
from deepeval.test_case import LLMTestCase

case = LLMTestCase(
    input="¿Cuál es la política de devoluciones?",
    actual_output="Puedes devolver cualquier producto en 30 días.",
    retrieval_context=["Política: devoluciones en 30 días desde la compra."],
)
```

**Paso 2: medir AnswerRelevancy**

`AnswerRelevancyMetric` evalúa si la respuesta es pertinente para la pregunta. El `threshold` define el mínimo aceptable — por debajo de ese valor, el test falla.

```python
from deepeval.metrics import AnswerRelevancyMetric

metric = AnswerRelevancyMetric(threshold=0.7)
metric.measure(case)

print(f"Score: {metric.score:.2f}")   # e.g. 0.82
print(f"Passed: {metric.is_test_case_passed()}")  # True
```

**Paso 3: combinar métricas con assert_test**

`assert_test` aplica todas las métricas de golpe y lanza una excepción si alguna falla. Es el patrón estándar para integrar evaluaciones en pytest.

```python
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
from deepeval.test_case import LLMTestCase

def test_respuesta_relevante_y_fiel():
    case = LLMTestCase(
        input="¿Cuál es la política de devoluciones?",
        actual_output="Puedes devolver cualquier producto en 30 días.",
        retrieval_context=["Política: devoluciones en 30 días desde la compra."],
    )
    assert_test(case, [
        AnswerRelevancyMetric(threshold=0.7),
        FaithfulnessMetric(threshold=0.7),
    ])
```

## Técnicas avanzadas

El módulo incluye dos utilidades propias (`src/threshold_checker.py` y `src/eval_antipatterns.py`) que complementan DeepEval para escenarios de producción más exigentes.

### Umbrales diferenciados por nivel de riesgo

Cuando tienes múltiples métricas y distintos productos con niveles de riesgo diferentes, necesitas umbrales diferenciados por contexto. Un chatbot de soporte interno tolera más errores que uno regulado en banca o salud. `QAGateChecker` encapsula esa lógica: defines el nivel de riesgo una vez y el checker aplica los thresholds correspondientes a cada métrica.

```python
from src.threshold_checker import QAGateChecker, RiskLevel

checker = QAGateChecker(risk_level=RiskLevel.HIGH_RISK)
results = checker.check({
    "faithfulness": 0.88,
    "answer_relevancy": 0.91,
    "refusal_rate": 0.97,
})
failed = [r for r in results if not r.passed]
# En HIGH_RISK: faithfulness≥0.90, answer_relevancy≥0.92, refusal_rate≥0.99
# → los tres scores anteriores fallan en HIGH_RISK
```

| Métrica | Mínimo | Target | Alto riesgo |
|---------|--------|--------|-------------|
| Faithfulness | 0.70 | 0.85 | 0.90 |
| Answer Relevancy | 0.75 | 0.90 | 0.92 |
| Context Recall | 0.70 | 0.85 | 0.90 |
| Answer Correctness | 0.65 | 0.80 | 0.88 |
| Refusal Rate | 0.95 | 0.98 | 0.99 |

### Validación del diseño de la evaluación

Antes de confiar en los resultados de tu evaluación, verifica que el diseño del test no tiene anti-patterns que invaliden las conclusiones. Un score alto en un dataset mal construido es una falsa garantía. `EvalDesignChecker` detecta los 10 problemas más frecuentes automáticamente.

```python
from src.eval_antipatterns import EvalDesignChecker

checker = EvalDesignChecker()
report = checker.check_all(
    test_cases=my_dataset,
    train_inputs=train_queries,
    baseline_score=0.85,
    n_samples=len(my_dataset),
    generator_model_id="claude-sonnet-4-6",
    judge_model_id="gpt-4o",
    threshold=0.70,
    latency_stats={"mean": 1.2, "p95": 2.8},
    n_runs=5,
    has_variance_report=True,
)
# report.passed = True si no hay violaciones CRITICAL ni HIGH
```

| AP | Anti-pattern | Severidad |
|----|-------------|-----------|
| AP-01 | Solo happy path (sin casos negativos) | HIGH |
| AP-02 | Test contaminado con datos de training | HIGH |
| AP-03 | Sin baseline de comparación | CRITICAL |
| AP-04 | Muestra insuficiente (< 30 casos) | HIGH |
| AP-05 | Mismo LLM como generador y juez | CRITICAL |
| AP-06 | Ignora distribución de producción | MEDIUM |
| AP-07 | Threshold arbitrario sin validación | MEDIUM |
| AP-08 | Sin edge cases ni adversariales | HIGH |
| AP-09 | Latencia sin percentiles (p95/p99) | HIGH |
| AP-10 | Reproducibilidad ignorada | HIGH |

## Errores comunes

❌ **Usar el mismo modelo como generador y como juez** — el juez favorece sus propias respuestas sistemáticamente, inflando los scores de forma artificial.
✅ Usar modelos distintos para generación y evaluación (ver AP-05 en la tabla anterior).

---

❌ **Threshold 0.7 "porque suena bien"** — sin base empírica el gate no tiene significado real; puedes estar bloqueando cambios buenos o dejando pasar cambios malos.
✅ Derivar el threshold de evaluaciones históricas sobre datos reales de producción.

---

❌ **Dataset solo con preguntas cuya respuesta está en el contexto** — no detecta fallos en queries ambiguas, out-of-scope o con contexto insuficiente.
✅ Incluir al menos 20% de casos negativos (respuesta incorrecta, contexto irrelevante, query ambigua).

---

❌ **Menos de 30 casos en el golden set** — los resultados son estadísticamente no significativos; una pequeña variación en el modelo puede cambiar el veredicto al azar.
✅ Mínimo 30 casos, recomendado 100+ para resultados estables.

## En producción

Los thresholds de CI deben escalar con el entorno: más estrictos cuanto más cerca estás del usuario real.

| Entorno    | AnswerRelevancy | Faithfulness |
|------------|----------------|--------------|
| PR         | ≥ 0.70         | ≥ 0.70       |
| Staging    | ≥ 0.80         | ≥ 0.82       |
| Producción | ≥ 0.85         | ≥ 0.88       |

Comando para ejecutar este módulo en CI (sin llamadas LLM reales):

```bash
pytest modules/01-primer-eval/tests/ -m "not slow" -q
```

Para monitorizar estos scores en producción a lo largo del tiempo → módulo 13.

## Caso real en producción

Una fintech española con chatbot de soporte para 40.000 clientes cambió el prompt de su asistente para mejorar el tono de las respuestas — menos formal, más cercano. El equipo de producto quedó satisfecho con la revisión manual de 15 ejemplos. Sin embargo, antes de desplegar a staging, el pipeline de CI ejecutó `assert_test` sobre el golden set de 120 casos reales.

`AnswerRelevancy` bajó de 0.82 a 0.61 en el cluster de queries sobre "cancelación de cuenta". El nuevo prompt era más amable, pero omitía la información clave sobre el proceso de cancelación — el modelo priorizaba el tono sobre la precisión. Con el threshold configurado a 0.75 en staging, el gate bloqueó automáticamente el despliegue.

El equipo ajustó el prompt para equilibrar tono e información, volvió a ejecutar la suite, y esta vez todos los clusters superaron el threshold. El fix tardó dos horas. Sin la métrica, el bug habría llegado a producción afectando a miles de usuarios que preguntaban cómo cancelar su cuenta — exactamente el tipo de query donde una respuesta incompleta genera frustración y llamadas al soporte humano.

## Ejercicios

- 🟢 **Básico** — Abre `modules/01-primer-eval/tests/test_first_eval.py`, cambia el `threshold` de `AnswerRelevancyMetric` a 0.95 y ejecuta `pytest modules/01-primer-eval/tests/ -m "not slow" -q`. ¿Cuántos tests fallan? ¿Por qué tiene sentido ese comportamiento?

- 🟡 **Intermedio** — Añade un tercer `LLMTestCase` donde el `actual_output` contenga información que NO está en el `retrieval_context`. Verifica que `FaithfulnessMetric` lo detecta como fallido.

- 🔴 **Avanzado** — Usa `QAGateChecker` con `RiskLevel.HIGH_RISK` sobre los resultados de 5 `LLMTestCase` diferentes. Identifica cuáles habrían bloqueado un despliegue en producción y explica por qué.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">50</div>
  <div class="stat-label">tests</div>
</div>

<div class="stat-card">
  <div class="stat-number">0.05s</div>
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
pytest modules/01-primer-eval/tests/ \
  -m "not slow" -q
```

<div class="module-next">
  <div class="next-label">Siguiente →</div>
  <a href="/modulos/02-ragas-basics">02 — ragas-basics</a>
</div>

</div>
</div>
