# Módulo 01 — Primer Eval con DeepEval

**Status:** implemented ✅

## Qué aprenderás

- Escribir tu primer `LLMTestCase` con DeepEval
- Usar `AnswerRelevancyMetric` y `FaithfulnessMetric`
- Ejecutar evaluaciones con `pytest` sin API keys externas (Ollama local o Groq free tier)
- Entender el output de DeepEval: score, reason, threshold

## Capítulo del manual

Cubre la sección 6.2 del manual (`docs/04-frameworks-oss.md` → DeepEval deep dive) y la sección 1.3 (pirámide de testing adaptada a IA).

## Cómo ejecutar

```bash
cd modules/01-primer-eval
uv sync --extra eval
pytest tests/ -v
# o con cassette (sin llamadas reales):
pytest tests/ -v --record-mode=none
```

## Requisitos

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) instalado
- Sin API key: el cassette pregrabado en `tests/cassettes/` cubre las llamadas
- Con Ollama: `ollama pull llama3.2` (modelos gratuitos locales)
- Con Groq: exporta `GROQ_API_KEY` (free tier, no tarjeta)

## Qué observar en el output

Cuando ejecutes los tests verás algo así:

```
PASSED tests/test_first_eval.py::test_answer_relevancy_basic
  AnswerRelevancyMetric: 0.82 (threshold: 0.7) ✓
  FaithfulnessMetric: 0.91 (threshold: 0.8) ✓
```

Fíjate en el **score numérico** (no solo pass/fail) y en el **reason** que da el juez LLM.

## Ejercicio propuesto

Modifica `tests/test_first_eval.py` para añadir un tercer test case donde la respuesta sea una alucinación obvia (invéntate datos). ¿Cuál de las dos métricas lo detecta primero? ¿Por qué?

*Pista: mira la definición de `FaithfulnessMetric` en `docs/04-frameworks-oss.md` y fíjate en qué datos necesita.*

## Estructura

```
01-primer-eval/
├── README.md
├── src/
│   └── simple_rag.py      # RAG mínimo de ejemplo
└── tests/
    ├── cassettes/          # respuestas grabadas para CI offline
    │   └── first_eval.yaml
    ├── conftest.py
    └── test_first_eval.py
```
