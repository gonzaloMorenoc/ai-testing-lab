# Glosario y referencias rápidas

> Parte del [Manual de Testing de Chatbots y LLMs](./manual-completo.md).

---

## 17. Referencias rápidas para tener abiertas

- DeepEval docs: [deepeval.com/docs](https://deepeval.com/docs/getting-started)
- RAGAS: [docs.ragas.io/en/stable/concepts/metrics/available_metrics](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/)
- Promptfoo: [promptfoo.dev/docs/intro](https://www.promptfoo.dev/docs/intro/)
- OWASP Top 10 LLM 2025: [genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025](https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/)
- Garak: [github.com/NVIDIA/garak](https://github.com/NVIDIA/garak)
- PyRIT: [github.com/Azure/PyRIT](https://github.com/Azure/PyRIT) + [AI Red Teaming Playground Labs](https://github.com/microsoft/AI-Red-Teaming-Playground-Labs)
- TruLens RAG Triad: [trulens.org/getting_started/core_concepts/rag_triad](https://www.trulens.org/getting_started/core_concepts/rag_triad/)
- Botium: [botium-docs.readthedocs.io](https://botium-docs.readthedocs.io/)
- Rasa testing: [rasa.com/docs/rasa-pro/nlu-based-assistants/testing-your-assistant](https://rasa.com/docs/rasa-pro/nlu-based-assistants/testing-your-assistant/)
- Giskard: [docs.giskard.ai](https://docs.giskard.ai/)
- Langfuse: [langfuse.com/docs](https://langfuse.com/docs)
- Phoenix: [github.com/Arize-ai/phoenix](https://github.com/Arize-ai/phoenix)
- LangSmith: [docs.langchain.com/langsmith/evaluation](https://docs.langchain.com/langsmith/evaluation)
- MLflow GenAI: [mlflow.org/docs/latest/genai/eval-monitor](https://mlflow.org/docs/latest/genai/eval-monitor/)
- ISTQB CT-AI v2.0: [istqb.org/certifications/certified-tester-ai-testing-ct-ai](https://istqb.org/certifications/certified-tester-ai-testing-ct-ai/)
- MT-Bench paper: [arxiv.org/abs/2306.05685](https://arxiv.org/abs/2306.05685)
- Chatbot Arena leaderboard: [lmarena.ai](https://lmarena.ai/)

---

### Cierre

Hay tres ideas que condensan todo lo anterior y vale la pena fijar:

1. **El LLM no es determinista, tu pipeline sí puede serlo.** Mete asserts deterministas donde puedas (schemas, regex, tools) y reserva el LLM-as-a-judge para las dimensiones semánticas con threshold, no con igualdad.
2. **Tu golden dataset vale más que cualquier framework.** Da igual si eliges DeepEval, RAGAS o LangSmith: sin un dataset diverso, versionado y alimentado con failures reales de producción, todas las métricas mienten con elegancia.
3. **La seguridad de LLMs ya no es opcional.** OWASP Top 10 LLM 2025, red teaming continuo, Garak/PyRIT en CI nightly y guardrails en runtime son baseline, igual que hoy es impensable shippear web apps sin SAST/DAST.

Con el stack que ya manejas (Python + pytest + Playwright + Robot + Karate), el paso natural es construir una suite de QA multicapa donde cada herramienta haga lo que mejor hace: Playwright para la UI real, DeepEval/RAGAS para la calidad semántica, Garak/DeepTeam para seguridad, y Langfuse o Phoenix como backbone de observabilidad. Ese combo —más el CT-AI v2.0 como sello formal— te deja en la posición rara y bien pagada de ser un SDET que entiende de verdad sistemas probabilísticos.

---

## Glosario de términos

| Término | Definición breve |
|---------|-----------------|
| **LLM** | Large Language Model — modelo de lenguaje de gran escala |
| **RAG** | Retrieval-Augmented Generation — arquitectura que combina recuperación de documentos con generación |
| **Faithfulness** | Métrica que mide si los claims de la respuesta están soportados por el contexto recuperado |
| **Answer Relevancy** | Métrica que mide cuán pertinente es la respuesta al input del usuario |
| **Context Precision** | Proporción de chunks recuperados que son relevantes, ponderada por ranking |
| **Context Recall** | Cobertura del contexto recuperado respecto a la respuesta ideal |
| **LLM-as-a-judge** | Técnica de evaluación que usa un modelo fuerte para puntuar las salidas de otro modelo |
| **G-Eval** | Evaluador LLM-as-a-judge con chain-of-thought de DeepEval, basado en criterios en lenguaje natural |
| **DAG Metric** | Métrica de grafo acíclico dirigido para evaluaciones con lógica determinista |
| **Hallucination** | Respuesta inventada o no fundamentada en la información disponible |
| **Groundedness** | Propiedad de una respuesta que puede verificarse contra los documentos de contexto |
| **Prompt Injection** | Ataque en que instrucciones maliciosas sobreescriben el system prompt |
| **Jailbreak** | Técnica para eludir las restricciones de seguridad de un LLM |
| **Red teaming** | Proceso sistemático de encontrar vulnerabilidades en un sistema de IA |
| **Garak** | Scanner CLI de vulnerabilidades para LLMs (NVIDIA, Apache 2.0) |
| **PyRIT** | Framework de red teaming de Microsoft (MIT), soporta Crescendo multi-turno |
| **DeepTeam** | Capa de red teaming sobre DeepEval, automatiza OWASP Top 10 LLM |
| **RAGAS** | Framework de evaluación para RAG con métricas reference-free |
| **DeepEval** | Framework de evaluación pytest-native con 50+ métricas |
| **Promptfoo** | Herramienta CLI/YAML para regression testing de prompts |
| **Langfuse** | Plataforma OSS de observabilidad para LLMs (OTel) |
| **Phoenix** | Plataforma de observabilidad OSS de Arize (OTel) |
| **VCR / cassette** | Técnica para grabar y reproducir respuestas HTTP en tests, eliminando llamadas reales |
| **Golden dataset** | Dataset de referencia curado y versionado para evaluación offline |
| **TTFT** | Time to First Token — latencia hasta el primer token de la respuesta |
| **BLEU** | Métrica de precision de n-gramas, común en traducción automática |
| **ROUGE** | Métrica de recall de n-gramas, estándar en summarization |
| **BERTScore** | Métrica de similitud semántica basada en embeddings BERT |
| **Context window** | Cantidad máxima de tokens que un LLM puede procesar en una sola llamada |
| **OWASP Top 10 LLM** | Lista de las 10 vulnerabilidades más críticas en aplicaciones LLM (edición 2025) |
| **Drift** | Cambio gradual en la distribución de inputs u outputs a lo largo del tiempo |
| **PSI** | Population Stability Index — métrica estadística para detectar drift |
| **OTel / OpenTelemetry** | Estándar abierto para trazas, métricas y logs distribuidos |
| **Tool calling** | Capacidad de un LLM para invocar funciones externas con argumentos estructurados |
| **Trajectory evaluation** | Evaluación de la secuencia completa de pasos de un agente, no solo el resultado final |
| **NeMo Guardrails** | Sistema de guardrails conversacionales de NVIDIA usando Colang DSL |
| **Guardrails AI** | Librería Python para validación de inputs/outputs de LLMs |
| **CT-AI v2.0** | Certified Tester AI Testing v2.0 — certificación ISTQB para testing de sistemas IA |
| **Botium** | "El Selenium de los chatbots" — framework de testing multi-conector para chatbots |
| **SWE-Bench** | Benchmark de resolución real de issues GitHub para evaluar capacidades de coding |
| **MMLU** | Massive Multitask Language Understanding — benchmark de conocimiento general |
| **Chatbot Arena** | Leaderboard de preferencia humana basado en votación y ELO (lmarena.ai) |
