# LLM Testing Lab

> **763 tests · 20 independent pytest modules · zero API calls needed**
>
> RAG evaluation · LLM-as-judge · red teaming · guardrails · observability · drift monitoring · cost-aware QA · retrieval avanzado · chatbot testing · robustness · HITL · caso end-to-end

**20 módulos pytest que cubren todas las capas de calidad en LLMs — desde el primer `LLMTestCase` hasta un caso end-to-end completo (chatbot de aseguradora regulada). Sin llamadas a APIs para ejecutar la suite completa.**

[![CI](https://github.com/gonzaloMorenoc/ai-testing-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/gonzaloMorenoc/ai-testing-lab/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/gonzaloMorenoc/ai-testing-lab/branch/main/graph/badge.svg)](https://codecov.io/gh/gonzaloMorenoc/ai-testing-lab)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%20|%203.12-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Open in Dev Containers](https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/gonzaloMorenoc/ai-testing-lab)

---

**English summary:** A hands-on pytest lab covering every QA layer for LLM systems — from writing your first `LLMTestCase` to running a full end-to-end regulated chatbot case with incident, runbook and postmortem. 763 tests across 20 independent modules. Powered by DeepEval, RAGAS, Garak, Guardrails AI, OpenTelemetry, and our own implementations of cost-aware QA, advanced retrieval, IAA metrics, and robustness suites. No API key required to run the full suite.

> ⭐ **If this lab helped you, consider starring the repo** — it helps others discover it and motivates continued development.

---

## Por qué existe esto

La mayoría de guías de calidad para LLMs se quedan en "usa DeepEval" o "usa RAGAS". Este laboratorio va más lejos: muestra **cómo** funciona cada técnica de evaluación por dentro, dónde falla, y cómo combinarlas en un pipeline de QA real.

Cada módulo es independiente, se ejecuta en milisegundos con mocks deterministas y enseña un concepto concreto — desde escribir tu primer `LLMTestCase` hasta detectar drift semántico en producción.

---

## Quickstart

```bash
git clone https://github.com/gonzaloMorenoc/ai-testing-lab.git
cd ai-testing-lab
pip install deepeval pytest pytest-cov numpy
pytest modules/01-primer-eval/tests/ -m "not slow" -q
```

Resultado esperado:

```
.......... 10 passed in 0.08s
```

Sin API key. Sin cuenta de pago. Sin conexión a internet.

> Para los módulos marcados con `@pytest.mark.slow`, exporta un `GROQ_API_KEY` gratuito antes de ejecutar `pytest -m slow`.

---

## Ejecutar la suite completa

```bash
pytest modules/ -m "not slow and not redteam" -q
```

```
763 passed, 1 skipped in 1.6s
```

763 tests en 20 módulos sin una sola llamada a API.

---

## Módulos

| # | Módulo | Tests | Concepto clave |
|---|--------|:-----:|----------------|
| 01 | [primer-eval](modules/01-primer-eval/) | 50 | Primer `LLMTestCase` · AnswerRelevancy · Faithfulness · anti-patrones de evaluación |
| 02 | [ragas-basics](modules/02-ragas-basics/) | 11 | Pipeline RAGAS · faithfulness · context\_precision · recall |
| 03 | [llm-as-judge](modules/03-llm-as-judge/) | 36 | G-Eval · DAG Metric · position bias · verbosity bias · calibración |
| 04 | [multi-turn](modules/04-multi-turn/) | 29 | 7 métricas multi-turn · coreference resolution · topic tracking |
| 05 | [prompt-regression](modules/05-prompt-regression/) | 43 | CI gate pipeline · PromptRegistry · z-test · significación estadística |
| 06 | [hallucination-lab](modules/06-hallucination-lab/) | 23 | Extracción de claims · groundedness · detección de negaciones |
| 07 | [redteam-garak](modules/07-redteam-garak/) | 23 | 42 attack prompts · DAN · many-shot · token manipulation · hit rate |
| 08 | [redteam-deepteam](modules/08-redteam-deepteam/) | 32 | OWASP Top 10 LLM 2025 · taxonomía 3 ejes de inyección · bias demográfico |
| 09 | [guardrails](modules/09-guardrails/) | 23 | Detección de PII · validación de output · pipeline I/O |
| 10 | [agent-testing](modules/10-agent-testing/) | 38 | 9 métricas de agentes · tool accuracy · recovery rate · handoff humano |
| 11 | [playwright-streaming](modules/11-playwright-streaming/) | 8 | SSE streaming · E2E chatbot UI · servidor mock FastAPI |
| 12 | [observability](modules/12-observability/) | 22 | 20 campos de traza · OTel spans · decorador `@trace` · IR metrics |
| 13 | [drift-monitoring](modules/13-drift-monitoring/) | 31 | KS test · PSI · AlertHistory · detección de tendencias · bootstrap IC95 |
| 14 | [embedding-eval](modules/14-embedding-eval/) | 33 | NDCG@k · MRR@k · MAP@k · similitud coseno · centroid shift |
| 15 | [cost-aware-qa](modules/15-cost-aware-qa/) | 67 | Cap. 27 · 7 métricas de coste · CostReport · regresión Δ% por tipo de cambio |
| 16 | [retrieval-advanced](modules/16-retrieval-advanced/) | 66 | Cap. 29 · HyDE · hybrid search · reranking · self-RAG · gate ΔNDCG@5 ≥ +0.05 |
| 17 | [chatbot-testing](modules/17-chatbot-testing/) | 60 | Cap. 10 · 8 áreas operativas · intent, fallback, escalation, sesiones, recovery |
| 18 | [robustness-suite](modules/18-robustness-suite/) | 52 | Cap. 12 · 8 categorías de perturbación · 4 métricas · separado de red-team |
| 19 | [hitl-iaa](modules/19-hitl-iaa/) | 55 | Cap. 31 · Cohen κ · Krippendorff α · Fleiss κ · ICC · protocolo de calibración 6 fases |
| 20 | [end-to-end-case](modules/20-end-to-end-case/) | 68 | Apéndice D · caso chatbot aseguradora salud · ata todos los capítulos en un flujo real |
|   | **Total** | **770** | |

---

## Qué aprenderás

```
Pirámide de evaluación para LLMs
│
├── Métricas unitarias
│   ├── 01  LLMTestCase, AnswerRelevancy, Faithfulness
│   ├── 02  RAGAS: faithfulness, context_precision, context_recall
│   ├── 03  LLM-as-judge: G-Eval, calibración de position bias
│   └── 14  Similitud coseno con embeddings, regression checker
│
├── Conversación y regresión
│   ├── 04  Multi-turn: ConversationalTestCase, memoria de 8 turnos
│   ├── 05  Regresión de prompts: PromptRegistry, z-test de significación
│   └── 06  Alucinaciones: extracción de claims, groundedness con negaciones
│
├── Seguridad y safety
│   ├── 07  Red teaming: 42 attack prompts, hit rate por categoría
│   ├── 08  DeepTeam: OWASP Top 10 LLM 2025, riesgos de agencia
│   └── 09  Guardrails: detección de PII, pipeline de validación I/O
│
└── Monitorización en producción
    ├── 10  Evaluación de agentes: tool accuracy, puntuación de trayectorias
    ├── 11  E2E streaming: Playwright + SSE + FastAPI
    ├── 12  Observabilidad: OTel, Langfuse, Phoenix
    └── 13  Drift monitoring: PSI, AlertHistory, análisis de tendencias
```

---

## Estructura del repo

```
ai-testing-lab/
├── modules/          # 20 labs independientes (empieza por cualquiera)
├── demos/            # sistemas reales sobre los que testear (RAG, Streamlit, Rasa)
├── goldens/          # datasets de evaluación versionados
├── docs/             # manual por capítulos + glosario
├── exercises/        # soluciones por módulo
└── docker/           # Langfuse + Ollama + stack de demos
```

---

## Principios de diseño

- **Sin llamadas a APIs en los tests rápidos.** Cada módulo corre offline con mocks deterministas. Las llamadas LLM reales están detrás de `@pytest.mark.slow`.
- **Un concepto por módulo.** Cada lab enseña exactamente una técnica de evaluación. Puedes leerlos y ejecutarlos en cualquier orden.
- **Patrones de producción, no juguetes.** AlertHistory, detección de drift con PSI, calibración de position bias y evaluación AST-safe son patrones que usarías en producción.
- **pytest-nativo.** Si sabes pytest, ya sabes cómo ejecutar esto.

---

## Stack

| Herramienta | Para qué |
|-------------|----------|
| [DeepEval](https://deepeval.com) | Evaluación pytest-nativa, 50+ métricas, LLM-as-judge |
| [RAGAS](https://docs.ragas.io) | Métricas RAG sin referencia |
| [Promptfoo](https://promptfoo.dev) | Regresión de prompts, matrices YAML |
| [Garak](https://github.com/NVIDIA/garak) | Escáner de vulnerabilidades LLM (NVIDIA) |
| [Guardrails AI](https://guardrailsai.com) | Validación de I/O para LLMs |
| [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails) | Rails conversacionales (Colang DSL) |
| [Langfuse](https://langfuse.com) | Trazas, evaluación online (MIT, self-hostable) |
| [Phoenix](https://github.com/Arize-ai/phoenix) | Observabilidad OSS (OTel, auto-instrumentación) |

---

## Cómo contribuir

- **¿Una métrica no correlaciona con tu juicio humano?** Abre un issue con el caso concreto.
- **¿Tienes un ejemplo golden para añadir?** Sigue el formato de `goldens/README.md` y abre un PR.
- **¿Propones un módulo nuevo?** Abre un issue con el concepto y el módulo más cercano como referencia.
- **¿Corriges el manual?** Errores factuales o links rotos en `docs/` — PR directo.

No hay plantilla de PR obligatoria. Describir qué cambió y por qué es suficiente.

---

## Licencia

MIT © 2026 Gonzalo Moreno
