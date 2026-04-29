---
layout: home

hero:
  name: "LLM Testing Lab"
  text: "Testa tus LLMs como un profesional"
  tagline: "14 módulos pytest · RAG · red teaming · guardrails · observabilidad · drift. Sin API key. Sin conexión."
  image:
    src: /demo.svg
    alt: "142 tests pasando en 0.16s"
  actions:
    - theme: brand
      text: Empezar →
      link: /guia/instalacion
    - theme: alt
      text: Ver módulos
      link: /modulos/
    - theme: alt
      text: GitHub ↗
      link: https://github.com/gonzaloMorenoc/ai-testing-lab

features:
  - icon: 🔬
    title: Evaluación RAG completa
    details: Faithfulness, context precision y answer relevancy con RAGAS. LLM-as-judge con G-Eval y calibración de position bias. Embeddings coseno para regresión semántica.

  - icon: 🛡️
    title: Red teaming y seguridad
    details: 42 attack prompts en 7 categorías — DAN, encoding, many-shot, token manipulation e indirect injection. OWASP Top 10 LLM 2025. Guardrails de entrada y salida.

  - icon: 📡
    title: Observabilidad y drift
    details: Trazas OpenTelemetry con Langfuse y Phoenix. Detección de drift semántico con PSI y AlertHistory. Tendencias degrading / recovering / stable.

  - icon: ⚡
    title: Sin llamadas a APIs
    details: Todos los tests rápidos usan mocks deterministas — word overlap, embeddings con hashlib, AST-safe eval. La suite completa corre en 0.16s sin conexión.

  - icon: 🧩
    title: Módulos independientes
    details: Cada lab enseña exactamente un concepto. Puedes empezar por cualquier módulo según lo que necesites aprender o implementar en tu proyecto.

  - icon: 🐍
    title: pytest-nativo
    details: Si sabes pytest, ya sabes cómo ejecutar esto. Sin frameworks propietarios, sin CLIs especiales. Solo pytest y las librerías que ya conoces.
---

<div class="hero-badge">✓ 142 tests · 0.16s · sin API key</div>

## Quickstart

```bash
git clone https://github.com/gonzaloMorenoc/ai-testing-lab.git
cd ai-testing-lab
pip install deepeval pytest pytest-cov numpy
pytest modules/ -m "not slow and not redteam" -q
```

```
142 passed, 1 skipped in 0.16s
```

Sin API key. Sin cuenta de pago. Sin conexión a internet.

## Qué aprenderás

```
Pirámide de evaluación para LLMs
│
├── Métricas unitarias
│   ├── 01  LLMTestCase, AnswerRelevancy, Faithfulness
│   ├── 02  RAGAS: faithfulness, context_precision, context_recall
│   ├── 03  LLM-as-judge: G-Eval, calibración de position bias
│   └── 14  Similitud coseno, regression checker, centroid shift
│
├── Conversación y regresión
│   ├── 04  Multi-turn: ConversationalTestCase, memoria de 8 turnos
│   ├── 05  Regresión de prompts: PromptRegistry, z-test de significación
│   └── 06  Alucinaciones: extracción de claims, groundedness con negaciones
│
├── Seguridad y safety
│   ├── 07  Red teaming: 42 attack prompts, hit rate por categoría
│   ├── 08  DeepTeam: OWASP Top 10 LLM 2025, riesgos de agencia
│   └── 09  Guardrails: PII detection, pipeline de validación I/O
│
└── Producción
    ├── 10  Evaluación de agentes: tool accuracy, trayectorias
    ├── 11  E2E streaming: Playwright + SSE + FastAPI
    ├── 12  Observabilidad: OTel, Langfuse, Phoenix
    └── 13  Drift monitoring: PSI, AlertHistory, tendencias
```
