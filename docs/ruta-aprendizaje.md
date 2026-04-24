# Ruta de aprendizaje

> Parte del [Manual de Testing de Chatbots y LLMs](./manual-completo.md).

---

## 16. Ruta de aprendizaje concreta para tu perfil

Dado que ya tienes `llm-eval-lab` y `SmartErrorDebugger`:

**Fase 1 – consolidar (2-4 semanas)**
1. Añade `ConversationalTestCase` y multi-turn a `llm-eval-lab`.
2. Integra RAGAS `TestsetGenerator` para auto-generar 200+ goldens sobre SmartErrorDebugger.
3. Monta GitHub Action con DeepEval + caché + thresholds.
4. Empieza CT-AI v2.0 de ISTQB (3 días de curso + examen).

**Fase 2 – seguridad (3-4 semanas)**
5. Corre Garak y PyRIT contra tu endpoint FastAPI de SmartErrorDebugger.
6. Implementa DeepTeam OWASP Top 10 en CI como job separado (nightly, no per-PR).
7. Añade Guardrails AI para validar outputs (PII, JSON schema) y NeMo Guardrails para topic rails.

**Fase 3 – observabilidad (2-3 semanas)**
8. Instrumenta SmartErrorDebugger con Langfuse (OSS, self-host) o Phoenix.
9. Online evaluation: 5% sampling + RAGAS reference-free en producción.
10. Dashboard con drift sobre embedding space de queries.

**Fase 4 – UI/E2E y portfolio (2-3 semanas)**
11. Playwright tests contra Streamlit UI con streaming asserts + LLM-as-judge.
12. Robot Framework BDD layer que orquesta DeepEval + Playwright (aprovecha tu stack).
13. Empaqueta todo en un repo público: "End-to-end QA para RAG con Python, Playwright y DeepEval". Este es exactamente el tipo de portfolio que el mercado 2026 está pidiendo para roles de AI QA ([aitestingguide.com](https://aitestingguide.com/how-to-test-llm-applications/)).

**Fase 5 – agentes y voice (opcional, 4-6 semanas)**
14. Convierte `llm-eval-lab` en un evaluador para agentes LangGraph con ToolCallAccuracy + trajectory evaluation.
15. Explora voice testing: Hamming/Sipfront + Botium Speech Processing.

---

## Laboratorios relacionados

La ruta de aprendizaje del manual mapea directamente a los módulos del lab:

| Fase del manual | Módulos del lab |
|----------------|-----------------|
| Fase 1 – consolidar | 01, 02, 03, 04 |
| Fase 2 – seguridad | 07, 08, 09 |
| Fase 3 – observabilidad | 12, 13 |
| Fase 4 – UI/E2E | 05, 11 |
| Fase 5 – agentes | 10 |
