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

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">8</div>
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
