# ai-testing-lab

Testing de LLMs y chatbots — de la pirámide de testing clásica a evaluación semántica, red teaming y observabilidad.

[![CI](https://github.com/gonzaloMorenoc/ai-testing-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/gonzaloMorenoc/ai-testing-lab/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/gonzaloMorenoc/ai-testing-lab/branch/main/graph/badge.svg)](https://codecov.io/gh/gonzaloMorenoc/ai-testing-lab)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Open in Dev Containers](https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/gonzaloMorenoc/ai-testing-lab)

## Qué aprenderás

- Escribir tu primer `LLMTestCase` con DeepEval y ejecutarlo con pytest
- Evaluar un pipeline RAG con las 9 métricas de RAGAS (faithfulness, context recall, answer relevancy…)
- Construir un juez LLM (G-Eval, DAG Metric) con rúbricas custom
- Probar conversaciones multi-turno con `ConversationalTestCase`
- Detectar regresiones de prompts con Promptfoo: matrices YAML de prompts × modelos
- Detectar alucinaciones con `HallucinationMetric` y el RAG Triad de TruLens
- Escanear vulnerabilidades LLM con Garak (DAN, encoding, toxicity)
- Atacar y defender con DeepTeam y el OWASP Top 10 LLM 2025
- Añadir guardrails de I/O con NeMo Guardrails y Guardrails AI
- Evaluar agentes: `ToolCallAccuracy`, `AgentGoalAccuracy`, trajectory evaluation
- Escribir tests E2E de streaming en Playwright contra UIs de chatbot
- Instrumentar un pipeline con Langfuse/Phoenix y medir en producción (OTel)
- Detectar drift semántico con Evidently AI y alertar antes de que los usuarios lo noten

## Quickstart

```bash
git clone https://github.com/gonzaloMorenoc/ai-testing-lab.git
cd ai-testing-lab
pip install deepeval pytest pytest-recording pyyaml   # dependencias mínimas
pytest modules/01-primer-eval/tests/ -m "not slow"    # 8 tests, 0 llamadas LLM reales
pytest modules/02-ragas-basics/tests/ -m "not slow"   # 10 tests, métricas RAGAS mock
```

Ningún módulo requiere API key para sus tests rápidos. Para los tests marcados `@pytest.mark.slow` exporta `GROQ_API_KEY` (free tier) antes de ejecutar `pytest -m slow`.

## Mapa del repo

```
ai-testing-lab/
├── modules/                  # 14 labs numerados e independientes
│   ├── 01-primer-eval/       # ← empieza aquí ✅
│   ├── 02-ragas-basics/      # ✅
│   ├── 03-llm-as-judge/      # ✅
│   ├── 04-multi-turn/        # ✅
│   ├── 05-prompt-regression/ # ✅
│   ├── 06-hallucination-lab/ # ✅
│   ├── 07-redteam-garak/     # ✅
│   ├── 08-redteam-deepteam/  # ✅
│   ├── 09-guardrails/        # ✅
│   ├── 10-agent-testing/     # ✅
│   ├── 11-playwright-streaming/ # ✅
│   ├── 12-observability/     # ✅
│   ├── 13-drift-monitoring/  # ✅
│   └── 14-embedding-eval/    # ✅
├── demos/                    # sistemas bajo prueba (RAG, Streamlit, Rasa, bot vulnerable)
├── docs/                     # manual troceado por capítulos + glosario
├── goldens/                  # datasets de evaluación versionados
├── exercises/solutions/      # soluciones de los ejercicios de cada módulo
└── docker/compose.yml        # Langfuse + Ollama + demos
```

## Módulos

| # | Módulo | Tests | Estado | Concepto clave |
|---|--------|-------|--------|----------------|
| 01 | [primer-eval](modules/01-primer-eval/) | 8 | ✅ implementado | LLMTestCase · AnswerRelevancy · Faithfulness |
| 02 | [ragas-basics](modules/02-ragas-basics/) | 10 | ✅ implementado | RAGAS · faithfulness · context_precision · context_recall |
| 03 | [llm-as-judge](modules/03-llm-as-judge/) | 11 | ✅ implementado | G-Eval · DAG Metric · position bias · verbosity bias |
| 04 | [multi-turn](modules/04-multi-turn/) | 10 | ✅ implementado | ConversationalTestCase · KnowledgeRetention · historial |
| 05 | [prompt-regression](modules/05-prompt-regression/) | 11 | ✅ implementado | PromptRegistry · RegressionChecker · Promptfoo |
| 06 | [hallucination-lab](modules/06-hallucination-lab/) | 9 | ✅ implementado | claim extraction · groundedness · RAG Triad |
| 07 | [redteam-garak](modules/07-redteam-garak/) | 8 | ✅ implementado | DAN · encoding attacks · jailbreak · hit rate |
| 08 | [redteam-deepteam](modules/08-redteam-deepteam/) | 8 | ✅ implementado | OWASP Top 10 LLM 2025 · prompt injection · agency |
| 09 | [guardrails](modules/09-guardrails/) | 11 | ✅ implementado | PII detection · output validation · input/output pipeline |
| 10 | [agent-testing](modules/10-agent-testing/) | 9 | ✅ implementado | tool selection · trajectory evaluation · AgentGoalAccuracy |
| 11 | [playwright-streaming](modules/11-playwright-streaming/) | 8 | ✅ implementado | SSE streaming · E2E chatbot UI · FastAPI mock server |
| 12 | [observability](modules/12-observability/) | 8 | ✅ implementado | OTel spans · @trace decorator · latency · error tracking |
| 13 | [drift-monitoring](modules/13-drift-monitoring/) | 9 | ✅ implementado | PSI · semantic drift · alert rules |
| 14 | [embedding-eval](modules/14-embedding-eval/) | 13 | ✅ implementado | cosine similarity · centroid shift · semantic regression |

## Ejecutar todos los módulos implementados

```bash
# Módulos 01-14 juntos (120+ tests, ~0.1s, sin API key)
pytest modules/01-primer-eval/tests/ \
       modules/02-ragas-basics/tests/ \
       modules/03-llm-as-judge/tests/ \
       modules/04-multi-turn/tests/ \
       modules/05-prompt-regression/tests/ \
       modules/06-hallucination-lab/tests/ \
       modules/07-redteam-garak/tests/ \
       modules/08-redteam-deepteam/tests/ \
       modules/09-guardrails/tests/ \
       modules/10-agent-testing/tests/ \
       modules/11-playwright-streaming/tests/ \
       modules/12-observability/tests/ \
       modules/13-drift-monitoring/tests/ \
       modules/14-embedding-eval/tests/ \
       -m "not slow"
# El módulo 11 requiere playwright+fastapi instalados; sin ellos se omite automáticamente.
```

## Cómo contribuir

Tipos de contribución bienvenidos:

- **Reportar sesgo en una rúbrica**: si los scores de un evaluador no se correlacionan con tu juicio humano, abre un issue con el caso concreto.
- **Añadir un golden al dataset**: sigue el formato de `goldens/README.md` y abre un PR.
- **Proponer un módulo nuevo**: abre un issue con el concepto y el módulo más próximo como referencia.
- **Corregir el manual**: errores factuales o links rotos en `docs/`, PR directo.

No hay plantilla de PR obligatoria. Describir qué cambió y por qué es suficiente.

## Créditos

| Herramienta | Para qué |
|------------|---------|
| [DeepEval](https://deepeval.com) | Evaluación pytest-native, 50+ métricas, LLM-as-judge |
| [RAGAS](https://docs.ragas.io) | Métricas RAG reference-free (faithfulness, context recall…) |
| [Promptfoo](https://promptfoo.dev) | Regression testing de prompts, matrices YAML |
| [Garak](https://github.com/NVIDIA/garak) | Scanner de vulnerabilidades LLM (NVIDIA, Apache 2.0) |
| [PyRIT](https://github.com/Azure/PyRIT) | Red teaming framework (Microsoft, MIT) |
| [Botium](https://botium-docs.readthedocs.io) | Testing de chatbots conversacionales |
| [TruLens](https://www.trulens.org) | RAG Triad + OpenTelemetry |
| [Phoenix](https://github.com/Arize-ai/phoenix) | Observabilidad OSS (OTel, auto-instrumentation) |
| [Langfuse](https://langfuse.com) | Trazas, evaluación online, self-host (MIT) |
| [Guardrails AI](https://guardrailsai.com) | Validación de I/O de LLMs |
| [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails) | Rails conversacionales (Colang DSL) |

## Licencia

```
MIT © 2026 Gonzalo Moreno
```
