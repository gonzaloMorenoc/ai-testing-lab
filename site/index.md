---
layout: home

hero:
  name: "LLM Testing Lab"
  text: "QA de IA, listo para producción."
  tagline: "20 módulos pytest que cubren todo el ciclo de calidad de un sistema LLM — desde el primer LLMTestCase hasta un caso end-to-end completo con incidente, runbook y postmortem. Sin API key. Sin conexión."
  image:
    src: /demo.svg
    alt: "763 tests pasando en 1.6s"
  actions:
    - theme: brand
      text: Empezar
      link: /guia/instalacion
    - theme: alt
      text: Manual PDF (gratis)
      link: /manual
    - theme: alt
      text: GitHub
      link: https://github.com/gonzaloMorenoc/ai-testing-lab

features:
  - icon:
      src: /icons/flask.svg
      width: 24
      height: 24
    title: Evaluación RAG completa
    details: Faithfulness, context precision y answer relevancy con RAGAS. LLM-as-judge con G-Eval y calibración de position bias. NDCG, MRR y MAP para retrieval avanzado (HyDE, hybrid, reranking, self-RAG).

  - icon:
      src: /icons/shield-check.svg
      width: 24
      height: 24
    title: Red teaming y seguridad
    details: Suite OWASP LLM Top 10 (2025), 42 attack prompts en 7 categorías — DAN, encoding, many-shot, indirect injection. Guardrails de entrada/salida, canary tokens y detección de PII multilingüe.

  - icon:
      src: /icons/radar.svg
      width: 24
      height: 24
    title: Observabilidad y drift
    details: Trace schema de 20 campos · OpenTelemetry · Langfuse y Phoenix. Detección de drift semántico con KS test, PSI y bootstrap IC95. Alertas dobles (absoluto y estadístico).

  - icon:
      src: /icons/zap.svg
      width: 24
      height: 24
    title: Sin llamadas a APIs
    details: Todos los tests rápidos usan mocks deterministas — word overlap, embeddings con hashlib, AST-safe eval. La suite completa de 763 tests corre en 1.6 segundos sin conexión.

  - icon:
      src: /icons/boxes.svg
      width: 24
      height: 24
    title: 20 módulos independientes
    details: "Cada lab enseña exactamente un concepto. Empieza por el que te interesa — RAG, agentes, cost-aware, robustness, HITL — o recorre el caso end-to-end del módulo 20 para verlo todo conectado."

  - icon:
      src: /icons/terminal.svg
      width: 24
      height: 24
    title: pytest-nativo
    details: Si sabes pytest, ya sabes ejecutar esto. Sin frameworks propietarios, sin CLIs especiales, sin lock-in. Solo pytest y las librerías open-source que ya conoces.
---

<div class="hero-badge">2.ª edición · 20 módulos · 763 tests · 1,6 s</div>

## Quickstart

Clona, instala y ejecuta la suite completa en menos de un minuto:

```bash
git clone https://github.com/gonzaloMorenoc/ai-testing-lab.git
cd ai-testing-lab
pip install deepeval pytest pytest-cov numpy
pytest modules/ -m "not slow and not redteam" -q
```

Resultado esperado:

```text
763 passed, 1 skipped in 1.6s
```

Sin API key. Sin cuenta de pago. Sin conexión a internet.

## Por dónde entrar

Los 20 módulos se agrupan en cinco familias. No hay orden obligatorio: entra por la que necesites hoy.

<div class="home-familias">
  <a href="/modulos/#métricas-unitarias"><em>I</em><b>Métricas unitarias</b><i>El primer LLMTestCase, RAGAS, jueces LLM y similitud semántica.</i><span>01 · 02 · 03 · 14</span></a>
  <a href="/modulos/#conversación-y-regresión"><em>II</em><b>Conversación</b><i>Multi-turno, regresión de prompts y detección de alucinaciones.</i><span>04 · 05 · 06</span></a>
  <a href="/modulos/#seguridad-y-safety"><em>III</em><b>Seguridad</b><i>Red teaming con Garak y DeepTeam, guardrails de entrada y salida.</i><span>07 · 08 · 09</span></a>
  <a href="/modulos/#producción"><em>IV</em><b>Producción</b><i>Agentes, streaming, observabilidad, drift y coste por consulta.</i><span>10 → 15</span></a>
  <a href="/modulos/#disciplinas-avanzadas"><em>V</em><b>Avanzado</b><i>Retrieval, chatbots por área, robustez, anotadores y caso final.</i><span>16 → 20</span></a>
</div>

## Recorridos sugeridos

Tres formas de empezar según tu rol:

::: tip Si vienes de QA tradicional
Empieza por `01-primer-eval` y sigue la [ruta de aprendizaje](./guia/ruta). En 6 horas tendrás el vocabulario completo del QA de IA.
:::

::: tip Si construyes RAG en producción
Salta directamente a `02-ragas-basics` → `06-hallucination-lab` → `16-retrieval-advanced`. Después aplica la [Tabla maestra de umbrales](./guia/umbrales) en tu CI/CD.
:::

::: tip Si lideras un equipo
Lee el [modelo de madurez L1-L5](./guia/madurez), audita tu sistema contra el [marco normativo](./guia/marco-normativo) y reproduce el [caso end-to-end](./modulos/20-end-to-end-case) en una hora.
:::

## Recursos

- [Manual de QA para Sistemas de IA](/manual) — 193 páginas, 33 capítulos, 4 apéndices. PDF gratuito.
- [Tabla maestra de umbrales](./guia/umbrales) — gates canónicos de CI/CD
- [Quiz de 45 preguntas](./quiz/) — auto-evaluación de QA AI Engineer
- [Referencias bibliográficas](./referencias) — papers y frameworks citados
- [Índice alfabético](./indice) — ~180 términos con remisión al capítulo
