# Frameworks open source – comparación operativa

> Parte del [Manual de Testing de Chatbots y LLMs](./manual-completo.md).

---

## 6. Frameworks open source – comparación operativa

### 6.1 Tabla comparativa

| Framework | Tipo | Lenguaje | pytest nativo | Tracing | RAG metrics | Red team | Self-host |
|-----------|------|----------|---------------|---------|-------------|----------|-----------|
| **DeepEval** | Evaluation | Python | ✅ | Sí (Confident AI) | ✅ 14+ | ✅ DeepTeam | Local |
| **RAGAS** | RAG eval | Python | Parcial | No (integra Langfuse) | ✅ core | No | Local |
| **Promptfoo** | Eval + red team | JS/TS (CLI) | N/A (tiene GH Action) | Limitado | ✅ | ✅ | Local |
| **Giskard** | Testing + red team | Python | Parcial | Hub comercial | ✅ RAGET | ✅ | Local + Hub |
| **TruLens** | Eval + tracing | Python | No | ✅ OTel | ✅ RAG Triad | No | Local |
| **Phoenix** | Observability + eval | Python | No | ✅ OTel | ✅ | Parcial | ✅ |
| **LangSmith** | Observability + eval | Py/JS | ✅ | ✅ | ✅ templates | Templates | Enterprise tier |
| **Langfuse** | Observability + eval | Py/JS | Via SDK | ✅ OTel | Via RAGAS | No nativo | ✅ OSS |
| **MLflow genai** | Eval + tracking | Python | No | ✅ | ✅ | No | ✅ |
| **LangCheck** | Métricas NLP | Python | Sí | No | Parcial | No | Local |
| **Evidently AI** | ML monitoring + LLM | Python | Parcial | No | ✅ básico | No | ✅ |
| **UpTrain** | Eval | Python | No | Parcial | ✅ | No | ✅ |
| **Guardrails AI** | Output validation | Python | N/A | No | N/A | Parcial | ✅ |
| **NeMo Guardrails** | Dialog control | Python (Colang) | N/A | No | N/A | Parcial | ✅ |

### 6.2 Deep dive: DeepEval (el que mejor encaja con tu perfil)
Motivos por los que es la primera recomendación para un pytest + Python user:

- **`deepeval test run` se comporta como pytest**, con flags -n (parallel), -c (cache), -s (skip on missing param), -v (verbose) ([confident-ai.com](https://www.confident-ai.com/docs/llm-evaluation/unit-testing-cicd)).
- **End-to-end y component-level** (con `@observe`) con los mismos `LLMTestCase`/`ConversationalTestCase`.
- **Synthetic dataset generation** vía `Synthesizer`.
- **Benchmarks nativos**: MMLU, HellaSwag, DROP, TruthfulQA, HumanEval, GSM8K ([deepeval.com](https://deepeval.com/docs/benchmarks-introduction)).
- **50+ métricas** research-backed; G-Eval + DAG cubren casi cualquier caso custom.
- **Red teaming** via DeepTeam con framework=OWASP/MITRE/NIST.

Ejemplo mínimo pytest:
```python
import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
from deepeval.test_case import LLMTestCase
from deepeval.dataset import EvaluationDataset

dataset = EvaluationDataset()
dataset.add_goldens_from_csv_file("tests/goldens.csv", context_col_delimiter=";")

@pytest.mark.parametrize("test_case", dataset.test_cases)
def test_rag_pipeline(test_case: LLMTestCase):
    assert_test(test_case, [
        AnswerRelevancyMetric(threshold=0.7),
        FaithfulnessMetric(threshold=0.8),
    ])
```
Y en CLI: `deepeval test run tests/ -n 4 -c`.

### 6.3 RAGAS – el estándar de facto para RAG
Punto fuerte: métricas *reference-free* como faithfulness correlacionan 95% con anotadores humanos en WikiEval ([redis.io](https://redis.io/blog/get-better-rag-responses-with-ragas/)). API nueva (collections-based):
```python
from ragas.metrics.collections import Faithfulness
from ragas.llms import llm_factory
scorer = Faithfulness(llm=llm_factory("gpt-4o-mini", client=AsyncOpenAI()))
result = await scorer.ascore(user_input=..., response=..., retrieved_contexts=[...])
```
Integración limpia con Langfuse: envías `ragas_scores` como `create_score(trace_id=...)` ([langfuse.com](https://langfuse.com/guides/cookbook/evaluation_of_rag_with_ragas)).

### 6.4 Promptfoo – YAML declarativo y red team
Fuerte especialmente si tu equipo no es 100% Python. Config típica:
```yaml
prompts: [file://prompts/v1.txt, file://prompts/v2.txt]
providers: [openai:gpt-4o-mini, anthropic:claude-3-5-sonnet]
tests:
  - vars: {question: "¿Política de devoluciones?"}
    assert:
      - type: llm-rubric
        value: "Debe mencionar el plazo de 30 días"
      - type: contains-any
        value: ["30 días", "reembolso"]
```
`promptfoo eval` corre la matriz; `promptfoo redteam run` genera ataques automáticamente. Se integra en GitHub Actions con caché para controlar coste ([github.com/promptfoo/promptfoo-action](https://github.com/promptfoo/promptfoo-action)).

### 6.5 Giskard – testing + red teaming para empresa
Automatic scan de vulnerabilidades, RAGET (Retrieval-Augmented Generation Evaluation Toolkit) para auto-generar test cases desde tu knowledge base, y agentes multi-turn autónomos sobre 40+ probes. Bien alineado con EU AI Act ([giskard.ai](https://www.giskard.ai/), [appsecsanta.com](https://appsecsanta.com/giskard)).

### 6.6 TruLens – RAG Triad + OpenTelemetry
Introdujo las tres métricas más usadas en RAG: **context relevance, groundedness, answer relevance** ([trulens.org](https://www.trulens.org/getting_started/core_concepts/rag_triad/)). Ahora 100% OpenTelemetry, con semantic conventions propias. Viene con BEIR loader integrado para benchmarks IR (NDCG, hit rate, recall@k).

### 6.7 Phoenix (Arize, Elastic License 2.0)
100% OTel, auto-instrumentation para OpenAI Agents SDK, Claude Agent SDK, LangGraph, LlamaIndex, DSPy, Vercel AI SDK, Mastra, CrewAI ([github.com/Arize-ai/phoenix](https://github.com/Arize-ai/phoenix)). Probablemente la observabilidad OSS más completa sin commercial lock-in (aparte de Langfuse).

### 6.8 MLflow LLM evaluation
La opción natural si ya usas MLflow para ML clásico. `mlflow.genai.evaluate()` separa del `mlflow.models.evaluate()` legacy. Soporta `question-answering` model_type con métricas predefinidas, LLM-as-a-judge custom via `make_metric` y `genai.scorers.Correctness`/`Guidelines` ([mlflow.org](https://mlflow.org/docs/latest/genai/eval-monitor/)).

### 6.9 Pytest plugins y libraries adicionales
- `pytest-asyncio` para tests async con SDKs modernos.
- `pytest-xdist` para paralelizar calls.
- `hypothesis` para property-based testing de prompts (generar inputs con gramática).
- `pytest-recording` / `vcrpy` para grabar/reproducir respuestas LLM (clave para controlar coste en CI).

---

## Laboratorios relacionados

| Módulo | Descripción |
|--------|-------------|
| [01-primer-eval](../modules/01-primer-eval/) | DeepEval: LLMTestCase, pytest-native, cassettes |
| [02-ragas-basics](../modules/02-ragas-basics/) | RAGAS: métricas reference-free para RAG |
| [03-llm-as-judge](../modules/03-llm-as-judge/) | G-Eval y jueces LLM custom |
| [05-prompt-regression](../modules/05-prompt-regression/) | Promptfoo: matrices YAML, CLI, GitHub Action |
| [12-observability](../modules/12-observability/) | Langfuse y Phoenix: tracing OTel |
