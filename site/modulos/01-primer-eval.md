---
title: "01 — primer-eval"
---

# 01 — primer-eval

Tu primer `LLMTestCase` con DeepEval. Métricas AnswerRelevancy y Faithfulness con mocks deterministas.

<div class="module-layout">
<div class="module-main">

## Qué aprenderás

- Estructura de un `LLMTestCase`: `input`, `actual_output`, `retrieval_context`
- Cómo funciona `AnswerRelevancy` por dentro (word overlap con la query)
- Cómo funciona `Faithfulness` (¿la respuesta se puede inferir del contexto?)
- Cuándo un test de evaluación debe pasar y cuándo debe fallar

## Código de ejemplo

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

## Por qué importa

> Sin métricas, detectar regresiones en el prompt requiere revisión manual. Con `LLMTestCase` puedes automatizarlo en CI.

## Nuevas implementaciones (Manual QA AI v12)

**`QAGateChecker`** — tabla maestra de umbrales (Tabla 1.2) para 5 métricas clave en tres niveles de riesgo:

```python
from src.threshold_checker import QAGateChecker, RiskLevel

checker = QAGateChecker(risk_level=RiskLevel.HIGH_RISK)
results = checker.check({
    "faithfulness": 0.88,
    "answer_relevancy": 0.91,
    "refusal_rate": 0.97,
})
failed = [r for r in results if not r.passed]
# HIGH_RISK: faithfulness≥0.90, answer_relevancy≥0.92, refusal_rate≥0.99
```

| Métrica | Mínimo | Target | Alto riesgo |
|---------|--------|--------|-------------|
| Faithfulness | 0.70 | 0.85 | 0.90 |
| Answer Relevancy | 0.75 | 0.90 | 0.92 |
| Context Recall | 0.70 | 0.85 | 0.90 |
| Answer Correctness | 0.65 | 0.80 | 0.88 |
| Refusal Rate | 0.95 | 0.98 | 0.99 |

**`EvalDesignChecker`** — los 10 anti-patterns de evaluación (AP-01 a AP-10, Cap 19):

```python
from src.eval_antipatterns import EvalDesignChecker, AntiPatternSeverity

checker = EvalDesignChecker()
report = checker.check_all(
    test_cases=my_dataset,
    train_inputs=train_queries,
    baseline_score=0.85,
    n_samples=len(my_dataset),
    generator_model_id="claude-sonnet-4-6",
    judge_model_id="gpt-4o",          # distinto → AP-05 OK
    threshold=0.70,                    # empírico → AP-07 OK
    latency_stats={"mean": 1.2, "p95": 2.8},
    n_runs=5,
    has_variance_report=True,
)
# report.passed = True si no hay CRITICAL ni HIGH violations
# report.violations = () si diseño correcto
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
