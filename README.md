# ai-testing-lab

Testing de LLMs y chatbots — de la pirámide de testing clásica a evaluación semántica, red teaming y observabilidad.

[![CI](https://github.com/gmc-code/ai-testing-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/gmc-code/ai-testing-lab/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)

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
git clone https://github.com/gmc-code/ai-testing-lab.git
cd ai-testing-lab
make setup                          # uv sync --all-extras
make test-module MODULE=01          # 7 tests, 0 llamadas LLM reales
```

El módulo 01 no necesita API key — usa cassettes VCR pregrabados. Para módulos con LLM real, exporta `GROQ_API_KEY` (free tier) o `OLLAMA_BASE_URL` si tienes Ollama local.

## Mapa del repo

```
ai-testing-lab/
├── modules/            # 13 labs numerados e independientes
│   ├── 01-primer-eval/ # ← empieza aquí (status: implementado ✅)
│   ├── 02-ragas-basics/
│   └── ...
├── demos/              # sistemas bajo prueba (RAG, Streamlit, Rasa, bot vulnerable)
├── docs/               # manual troceado por capítulos + glosario
├── goldens/            # datasets de evaluación versionados
├── exercises/          # ejercicios + soluciones
└── docker/compose.yml  # Langfuse + Ollama + demos
```

## Módulos

| # | Módulo | Estado | Capítulo del manual |
|---|--------|--------|---------------------|
| 01 | [primer-eval](modules/01-primer-eval/) | ✅ implementado | [04 — Frameworks OSS: DeepEval](docs/04-frameworks-oss.md) |
| 02 | [ragas-basics](modules/02-ragas-basics/) | 🔲 planned | [03 — Métricas](docs/03-metricas.md) |
| 03 | [llm-as-judge](modules/03-llm-as-judge/) | 🔲 planned | [03 — Métricas: LLM-as-judge](docs/03-metricas.md) |
| 04 | [multi-turn](modules/04-multi-turn/) | 🔲 planned | [02 — Tipos de testing](docs/02-tipos-de-testing.md) |
| 05 | [prompt-regression](modules/05-prompt-regression/) | 🔲 planned | [04 — Frameworks OSS: Promptfoo](docs/04-frameworks-oss.md) |
| 06 | [hallucination-lab](modules/06-hallucination-lab/) | 🔲 planned | [03 — Métricas: Faithfulness](docs/03-metricas.md) |
| 07 | [redteam-garak](modules/07-redteam-garak/) | 🔲 planned | [06 — Red teaming y OWASP](docs/06-red-teaming-y-owasp.md) |
| 08 | [redteam-deepteam](modules/08-redteam-deepteam/) | 🔲 planned | [06 — Red teaming y OWASP](docs/06-red-teaming-y-owasp.md) |
| 09 | [guardrails](modules/09-guardrails/) | 🔲 planned | [06 — Red teaming y OWASP](docs/06-red-teaming-y-owasp.md) |
| 10 | [agent-testing](modules/10-agent-testing/) | 🔲 planned | [12 — Tendencias: Agentic AI](docs/12-tendencias.md) |
| 11 | [playwright-streaming](modules/11-playwright-streaming/) | 🔲 planned | [09 — Playwright UI](docs/09-playwright-ui.md) |
| 12 | [observability](modules/12-observability/) | 🔲 planned | [12 — Tendencias: Observabilidad](docs/12-tendencias.md) |
| 13 | [drift-monitoring](modules/13-drift-monitoring/) | 🔲 planned | [11 — Buenas prácticas](docs/11-buenas-practicas.md) |

## Cómo contribuir

Tipos de contribución bienvenidos:

- **Implementar un módulo planned**: abre un issue con el número de módulo y tu propuesta de diseño antes de empezar.
- **Reportar sesgo en una rúbrica**: si los scores de un evaluador no se correlacionan con tu juicio humano, abre un issue con el caso concreto.
- **Añadir un golden al dataset**: sigue el formato de `goldens/README.md` y abre un PR.
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
