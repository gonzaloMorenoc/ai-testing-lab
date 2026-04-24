# Fundamentos de QA para IA

> Parte del [Manual de Testing de Chatbots y LLMs](./manual-completo.md).

---

## 1. Cómo encajar testing de IA en un background de QA clásico

### 1.1 Qué cambia respecto a testing tradicional
El primer shock mental es abandonar la idea de "mismo input → mismo output". Un LLM es estocástico: misma pregunta, distinta respuesta. Esto rompe aserciones exactas y obliga a pensar en **umbrales de calidad** y **distribuciones** en vez de pass/fail binario. Playwright, Selenium o Karate siguen siendo útiles para la capa de UI/API, pero la validación del contenido generado necesita otra caja de herramientas ([aitestingguide.com](https://aitestingguide.com/how-to-test-llm-applications/)).

Las diferencias concretas que importan para el diseño de pruebas:

- **No determinismo**: hay que repetir, muestrear, medir varianza.
- **Oracle problem**: a menudo no existe un "resultado esperado" único. Se sustituye por rúbricas, referencias aproximadas o *LLM-as-a-judge*.
- **Alto coste por test**: cada caso suele implicar llamadas a APIs de pago. El diseño del pipeline tiene que priorizar caché, batching y ejecución selectiva.
- **Superficie de ataque nueva**: prompt injection, jailbreaks, data leakage, alucinaciones, *excessive agency* en agentes ([genai.owasp.org](https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/)).

### 1.2 Certificación: ISTQB CT-AI v2.0
ISTQB lanzó la versión 2.0 del **Certified Tester AI Testing (CT-AI)**, que ahora se concentra completamente en probar sistemas basados en IA (la parte de "usar IA para testing" se movió al CT-GenAI). Incluye capítulos dedicados a LLMs y técnicas como exploratory testing y red teaming, con duración recomendada de 3 días ([istqb.org](https://istqb.org/istqb-releases-certified-tester-ai-testing-ct-ai-syllabus-version-2-0/), [istqb.org](https://istqb.org/certifications/certified-tester-ai-testing-ct-ai/)). Para un Senior QA con ISTQB Foundation, es el siguiente paso lógico y complementa bien lo que aprendiste en tu `llm-eval-lab`.

### 1.3 Pirámide de testing adaptada a IA
Una pirámide razonable para sistemas LLM:

| Capa | Qué validar | Herramientas |
|------|-------------|--------------|
| **Unit (prompts / componentes)** | Templates de prompt, funciones de retrieval, tool schemas | pytest + DeepEval component-level, Promptfoo |
| **Integration (pipeline)** | RAG end-to-end, encadenamiento de tools, guardrails | RAGAS, DeepEval, TruLens |
| **System / E2E** | UI del chatbot, widgets embebidos, flujos multi-turn | Playwright, Botium, Rasa test |
| **Seguridad / Red team** | Prompt injection, jailbreaks, PII leakage | Garak, PyRIT, DeepTeam, Giskard |
| **Observabilidad en producción** | Drift, métricas online, feedback humano | Langfuse, Phoenix, LangSmith, Helicone |

---

## Laboratorios relacionados

| Módulo | Descripción |
|--------|-------------|
| [01-primer-eval](../modules/01-primer-eval/) | Pirámide de testing en práctica: primer LLMTestCase con métricas |
| [05-prompt-regression](../modules/05-prompt-regression/) | Regression testing de prompts con Promptfoo |
