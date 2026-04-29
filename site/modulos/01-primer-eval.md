# 01 — primer-eval

**Concepto:** Tu primer `LLMTestCase` con DeepEval. Métricas AnswerRelevancy y Faithfulness con mocks deterministas.

**Tests:** 8 · **Tiempo:** ~0.05s · **API key:** no necesaria

## Qué aprenderás

- Estructura de un `LLMTestCase`: `input`, `actual_output`, `retrieval_context`
- Cómo funciona `AnswerRelevancy` por dentro (word overlap con la query)
- Cómo funciona `Faithfulness` (¿la respuesta se puede inferir del contexto?)
- Cuándo un test de evaluación debe pasar y cuándo debe fallar

## Ejecutar

```bash
pytest modules/01-primer-eval/tests/ -m "not slow" -q
```

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

Sin métricas, la única forma de saber si un cambio en el prompt mejoró o empeoró el sistema es comparar manualmente. Con `LLMTestCase` puedes detectar regresiones automáticamente en CI.
