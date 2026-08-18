---
title: "Manual de QA para Sistemas de Inteligencia Artificial"
pageClass: manual-page
aside: false
description: "193 páginas sobre testing de LLMs, RAG, chatbots y agentes. Segunda edición 2026. Descarga gratuita en PDF."
head:
  - - meta
    - property: og:type
      content: book
  - - meta
    - property: og:title
      content: "Manual de QA para Sistemas de Inteligencia Artificial"
  - - meta
    - property: og:description
      content: "193 páginas · 33 capítulos · 4 apéndices. LLMs, RAG, chatbots y agentes: métricas, red teaming, quality gates y un caso end-to-end completo. Descarga gratuita."
  - - meta
    - property: og:image
      content: https://ai-testing-lab.vercel.app/og-manual.png
  - - meta
    - property: og:url
      content: https://ai-testing-lab.vercel.app/manual
  - - meta
    - name: twitter:card
      content: summary_large_image
  - - meta
    - name: twitter:title
      content: "Manual de QA para Sistemas de Inteligencia Artificial"
  - - meta
    - name: twitter:description
      content: "193 páginas sobre testing de LLMs, RAG, chatbots y agentes. Descarga gratuita."
  - - meta
    - name: twitter:image
      content: https://ai-testing-lab.vercel.app/og-manual.png
---

<div class="manual-hero">
  <div>
    <p class="manual-eyebrow">Edición profesional · 2026</p>
    <h1>Manual de QA para <em>Sistemas de Inteligencia Artificial</em></h1>
    <p class="manual-sub">LLMs · RAG · Chatbots · Agentes</p>
    <div class="manual-meta">
      <span>193 páginas</span>
      <span>33 capítulos</span>
      <span>4 apéndices</span>
      <span>Segunda edición</span>
    </div>
    <div class="manual-actions">
      <a class="manual-btn manual-btn-primary" href="/manual-qa-ia.pdf" download="Manual-QA-Sistemas-IA-2026.pdf">↓ Descargar PDF (859 KB)</a>
      <a class="manual-btn manual-btn-ghost" href="/manual-qa-ia.pdf" target="_blank" rel="noopener">Leer en el navegador</a>
    </div>
  </div>
  <img class="manual-cover" src="/manual-portada.png" alt="Portada del Manual de QA para Sistemas de Inteligencia Artificial" />
</div>

## Qué es

Un manual de referencia para probar sistemas de IA generativa en producción. Cubre el ciclo completo: qué medir en cada tipo de sistema, con qué herramienta, qué umbral poner en el gate de CI y qué hacer cuando el gate se pone en rojo.

No es un catálogo de herramientas ni una introducción a los LLMs. Asume que ya tienes un sistema delante y una fecha de entrega, y está escrito para llevarte de «¿qué tengo aquí?» a «este es mi plan de pruebas» sin pasar por tres meses de investigación.

Este manual es la base teórica de **[los 20 módulos de este lab](/modulos/)**: cada técnica que se explica aquí tiene su implementación ejecutable en `modules/`, con tests que puedes correr en tu máquina.

## Contenido

<div class="manual-parts">
  <div class="manual-part">
    <div class="manual-part-num">Parte I · Cap. 1-3</div>
    <h4>Fundamentos</h4>
    <p>IA generativa, fundamentos técnicos de los LLMs, riesgos y marco normativo.</p>
  </div>
  <div class="manual-part">
    <div class="manual-part-num">Parte II · Cap. 4-5</div>
    <h4>El cambio de paradigma en QA</h4>
    <p>Por qué QA de IA no es QA tradicional. Taxonomía de sistemas conversacionales.</p>
  </div>
  <div class="manual-part">
    <div class="manual-part-num">Parte III · Cap. 6-9</div>
    <h4>RAG y evaluación de la generación</h4>
    <p>Retrieval-Augmented Generation, métricas RAGAS, LLM-as-judge y golden datasets.</p>
  </div>
  <div class="manual-part">
    <div class="manual-part-num">Parte IV · Cap. 10-13</div>
    <h4>Calidad conversacional y robustez</h4>
    <p>Testing de chatbots, similitud semántica, perturbaciones y deriva semántica.</p>
  </div>
  <div class="manual-part">
    <div class="manual-part-num">Parte V · Cap. 14-17</div>
    <h4>Seguridad, contexto y alucinaciones</h4>
    <p>OWASP LLM Top 10 (2025), prompt injection, evaluación multi-turno y detección de alucinaciones.</p>
  </div>
  <div class="manual-part">
    <div class="manual-part-num">Parte VI · Cap. 18-20</div>
    <h4>Operación y herramientas</h4>
    <p>CI/CD y quality gates, observabilidad y trazabilidad, RAGAS · TruLens · DeepEval.</p>
  </div>
  <div class="manual-part">
    <div class="manual-part-num">Parte VII · Cap. 21-23</div>
    <h4>Agentes, antipatrones y estrategia</h4>
    <p>Testing de agentes y sistemas multi-agente, antipatrones frecuentes y estrategia integral.</p>
  </div>
  <div class="manual-part">
    <div class="manual-part-num">Parte VIII · Cap. 24-33</div>
    <h4>Disciplinas especializadas</h4>
    <p>Prompt regression, bias y toxicity, cost-aware QA, PII leakage, retrieval avanzado, function calling, human-in-the-loop, reproducibilidad y glosario.</p>
  </div>
</div>

### Apéndices

| | |
|---|---|
| **A** | 45 preguntas de consolidación técnica, con respuesta |
| **B** | Referencias y lecturas recomendadas |
| **C** | Índice alfabético |
| **D** | Caso práctico end-to-end: chatbot RAG regulado |

## Por dónde empezar

El manual admite dos modos de lectura —guía de arranque o referencia— y propone tres rutas según de dónde vengas:

- **Tengo un sistema y una fecha de entrega.** Guía de arranque → la ficha de tu tipo de sistema → los capítulos que esa ficha señale → Apéndice D para verlo completo.
- **Vengo de QA clásico.** Parte I (cap. 1-3) → capítulo 4, que explica qué cambia exactamente → guía de arranque.
- **Preparo una entrevista de AI Quality Engineer.** Apéndice A (45 preguntas) + el glosario del capítulo 33.

La **guía de arranque** es deliberadamente mínima: clasificas tu sistema en una de cinco ramas (LLM puro, RAG, chatbot conversacional, agente, multimodal) y cada ficha responde siete preguntas —qué medir primero, con qué herramientas, qué golden dataset mínimo necesitas, qué gate poner en CI, los fallos más frecuentes, qué puedes dejar para después y en qué capítulos ampliar.

## Del manual al código

Cada parte del manual tiene módulos ejecutables en el lab:

| Manual | Módulos del lab |
|---|---|
| Parte III · RAG y evaluación | [01](/modulos/01-primer-eval), [02](/modulos/02-ragas-basics), [03](/modulos/03-llm-as-judge), [16](/modulos/16-retrieval-advanced) |
| Parte IV · Conversacional y robustez | [04](/modulos/04-multi-turn), [13](/modulos/13-drift-monitoring), [17](/modulos/17-chatbot-testing), [18](/modulos/18-robustness-suite) |
| Parte V · Seguridad | [07](/modulos/07-redteam-garak), [08](/modulos/08-redteam-deepteam), [09](/modulos/09-guardrails) |
| Parte VI · Operación | [12](/modulos/12-observability), [15](/modulos/15-cost-aware-qa) |
| Parte VII · Agentes | [10](/modulos/10-agent-testing) |
| Apéndice D · Caso end-to-end | [20](/modulos/20-end-to-end-case) |

## Descarga

<div class="manual-actions" style="margin: 1.5rem 0;">
  <a class="manual-btn manual-btn-primary" href="/manual-qa-ia.pdf" download="Manual-QA-Sistemas-IA-2026.pdf">↓ Descargar PDF (859 KB)</a>
  <a class="manual-btn manual-btn-ghost" href="https://github.com/gonzaloMorenoc/ai-testing-lab/releases/latest" target="_blank" rel="noopener">Ver en GitHub Releases</a>
</div>

PDF de 859 KB, con índice navegable y enlaces internos entre capítulos. Sin registro ni formulario.

## Aviso legal

Obra independiente publicada por su autor. **No es material oficial, acreditado ni avalado por ISTQB®** ni por ninguna de sus organizaciones miembro, y no prepara para certificaciones oficiales; las referencias a los syllabus *ISTQB® CT-AI v1.0* y *CT-GenAI v1.0* se hacen con fines de cita académica bajo el derecho de cita (art. 32 LPI).

Los umbrales, métricas y ejemplos son orientativos: cada equipo debe calibrarlos contra su baseline, dominio y nivel de riesgo.

© 2026 Gonzalo Moreno Cominero. Todos los derechos reservados. Se permite la descarga y el uso personal; queda prohibida la reproducción total o sustancial sin autorización escrita del autor, salvo citas breves con atribución.
