# Ruta de aprendizaje

Los módulos son independientes, pero esta secuencia está pensada para ir de menos a más complejidad.

## Ruta completa (orden recomendado)

### Semana 1 — Fundamentos de evaluación
1. [**01 — primer-eval**](/modulos/01-primer-eval): Tu primer `LLMTestCase`. AnswerRelevancy y Faithfulness.
2. [**02 — ragas-basics**](/modulos/02-ragas-basics): Pipeline RAG completo. Faithfulness, context precision y recall con RAGAS.
3. [**03 — llm-as-judge**](/modulos/03-llm-as-judge): Jueces LLM con G-Eval. Position bias y cómo calibrarlo.

### Semana 2 — Evaluación avanzada
4. [**04 — multi-turn**](/modulos/04-multi-turn): Conversaciones de múltiples turnos. Retención de información a lo largo de 8 turnos.
5. [**05 — prompt-regression**](/modulos/05-prompt-regression): Detectar regresiones cuando cambias un prompt. Significación estadística.
6. [**06 — hallucination-lab**](/modulos/06-hallucination-lab): Extracción de claims y groundedness. Detección de negaciones.
7. [**14 — embedding-eval**](/modulos/14-embedding-eval): Similitud semántica con embeddings. Regresión y detección de drift a nivel de corpus.

### Semana 3 — Seguridad
8. [**07 — redteam-garak**](/modulos/07-redteam-garak): 42 attack prompts en 7 categorías. Scanner de vulnerabilidades.
9. [**08 — redteam-deepteam**](/modulos/08-redteam-deepteam): OWASP Top 10 LLM 2025. Riesgos de agencia.
10. [**09 — guardrails**](/modulos/09-guardrails): Pipeline de validación de entrada y salida. Detección de PII.

### Semana 4 — Producción
11. [**10 — agent-testing**](/modulos/10-agent-testing): Evaluación de agentes. Tool accuracy y trayectorias.
12. [**11 — playwright-streaming**](/modulos/11-playwright-streaming): Tests E2E de UIs de chatbot con streaming SSE.
13. [**12 — observability**](/modulos/12-observability): Trazas OTel, Langfuse y Phoenix.
14. [**13 — drift-monitoring**](/modulos/13-drift-monitoring): PSI, AlertHistory y detección de tendencias.

---

## Rutas por objetivo

### Tengo un pipeline RAG y quiero medirlo
→ Módulos 01 → 02 → 03 → 06 → 14

### Quiero saber si mi modelo es vulnerable a ataques
→ Módulos 07 → 08 → 09

### Tengo el modelo en producción y quiero monitorizarlo
→ Módulos 12 → 13 → 14

### Quiero testear un agente con herramientas
→ Módulos 01 → 10

### Quiero hacer tests de regresión cuando cambio los prompts
→ Módulos 05 → 03
