# Tipos de sistemas y testing para IA

> Parte del [Manual de Testing de Chatbots y LLMs](./manual-completo.md).

---

## 2. Tipos de sistemas bajo prueba

1. **LLMs generativos puros** (ChatGPT, Claude, Gemini, modelos locales vía Ollama).
2. **RAG** – retriever + generator. Evaluación divide en *retriever metrics* (context precision/recall/relevancy) y *generator metrics* (faithfulness, answer relevancy) ([confident-ai.com](https://www.confident-ai.com/blog/rag-evaluation-metrics-answer-relevancy-faithfulness-and-more)).
3. **Chatbots rule-based / intent-based** (Rasa, Dialogflow, IBM Watson Assistant, Microsoft Bot Framework, Amazon Lex). Aquí la NLU es la pieza crítica: precisión de clasificación de intents y extracción de entidades ([rasa.com](https://rasa.com/docs/rasa-pro/nlu-based-assistants/testing-your-assistant/)).
4. **Híbridos** – mezcla de reglas deterministas + fallback a LLM.
5. **Agentes con tool calling** – evaluación en dos niveles: *end-to-end* (¿completó la tarea?) y *component-level* (¿eligió la tool correcta con los argumentos correctos?) ([confident-ai.com](https://www.confident-ai.com/blog/llm-agent-evaluation-complete-guide)).
6. **Voice assistants** – pipeline STT → LLM → TTS; cada etapa tiene métricas propias ([hamming.ai](https://hamming.ai/blog/the-ultimate-guide-to-asr-stt-tts-for-voice-agents)).
7. **Multimodales** – texto + imagen + audio; RAGAS ya incluye `MultimodalFaithfulness` y `MultimodalRelevance` ([docs.ragas.io](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/)).

---

## 3. Tipos de testing para IA/chatbots

### 3.1 Testing funcional y de flujos conversacionales
Validación de intents, entidades y slot filling. En Rasa se hace con el comando `rasa test` que evalúa NLU y dialogue por separado, reporta F1, matriz de confusión y stories fallidas en `failed_stories.md` ([legacy-docs-oss.rasa.com](https://legacy-docs-oss.rasa.com/docs/rasa/2.x/testing-your-assistant/), [blog.rasa.com](https://blog.rasa.com/rasa-automated-tests/)). En Rasa Pro 3.x se añaden aserciones tipo `generative_response_is_relevant` para flujos con LLM ([rasa.com](https://rasa.com/docs/rasa-pro/nlu-based-assistants/testing-your-assistant/)).

### 3.2 NLU/NLP testing
Para chatbots tradicionales: **accuracy de intent classification**, **F1 por intent**, **entity extraction precision/recall**, **confusion matrix**. Rasa expone esto nativamente con cross-validation (`rasa data split`, `rasa test nlu`) ([legacy-docs-oss.rasa.com](https://legacy-docs-oss.rasa.com/docs/rasa/2.x/testing-your-assistant/)).

### 3.3 Calidad de respuesta (relevance, coherence, fluency)
Para generative: se usan *LLM-as-a-judge* (G-Eval, RAGAS answer relevancy) y métricas clásicas BLEU/ROUGE/METEOR/BERTScore como *baseline*.

### 3.4 Alucinación y groundedness (RAG)
- **Hallucination** (respuesta inventada sin base) se mide con `HallucinationMetric` de DeepEval o con el *RAG Triad* de TruLens (context relevance, groundedness, answer relevance) ([trulens.org](https://www.trulens.org/getting_started/core_concepts/rag_triad/)).
- **Faithfulness** (RAGAS) descompone la respuesta en claims y verifica cuántos se infieren del contexto recuperado. Existe también `FaithfulnesswithHHEM` que usa el clasificador Vectara HHEM-2.1-Open, pequeño y gratis, útil para producción ([docs.ragas.io](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/)).

### 3.5 Context retention / multi-turn
DeepEval tiene `ConversationalTestCase`, `KnowledgeRetentionMetric`, `ConversationCompletenessMetric` y `ConversationalRelevancyMetric` ([deepeval.com](https://deepeval.com/docs/evaluation-introduction)). Rasa evalúa stories completas. Para RAG con memoria, RAGAS incluye `TopicAdherence` y `AgentGoalAccuracy`.

### 3.6 Regression testing de prompts y modelos
Promptfoo está específicamente pensado para esto: un `promptfooconfig.yaml` declarativo con prompts × modelos × casos, y comparación matricial en web UI ([promptfoo.dev](https://www.promptfoo.dev/docs/intro/), [medium.com](https://medium.com/@yukinagae/generative-ai-evaluation-with-promptfoo-a-comprehensive-guide-e23ea95c1bb7)). DeepEval + pytest + Confident AI muestra diffs con runs previos en rojo/verde ([deepeval.com](https://deepeval.com/docs/getting-started)).

### 3.7 Performance: latency, throughput, tokens
- **TTFT** (time to first token) y **p95 latency** para UX conversacional (voice requiere <500ms) ([inworld.ai](https://inworld.ai/resources/how-to-evaluate-tts-models)).
- **Tokens por segundo** y **coste por conversación**.
- Helicone o Langfuse capturan esto como span attributes vía OpenTelemetry ([helicone.ai](https://www.helicone.ai/blog/the-complete-guide-to-LLM-observability-platforms)).

### 3.8 Carga
Locust / k6 contra el endpoint del chatbot; Botium soporta ejecución bulk para concurrency y regresión a escala ([cekura.ai](https://www.cekura.ai/blogs/best-chatbot-testing-platforms)).

### 3.9 Seguridad, bias, toxicidad, robustez
Ver sección 5 (OWASP / red teaming).

### 3.10 A/B testing de prompts y modelos
Promptfoo (matriz), Braintrust (datasets + scorers + deployment blocking) o `ArenaGEval` de DeepEval permiten comparar variantes con *pairwise* ([deepeval.com](https://deepeval.com/docs/evaluation-prompts)). LangSmith soporta *pairwise evaluators* con LLM-as-a-judge custom ([blog.langchain.com](https://blog.langchain.com/pairwise-evaluations-with-langsmith/)).

### 3.11 Tool/function calling y agentes
Métricas clave: `ToolCallAccuracy`, `ToolCallF1`, `AgentGoalAccuracy` (RAGAS). Se evalúa tanto el *trajectory* (secuencia de steps) como el resultado final. LangSmith tiene templates específicos para "trajectory" y "tool call" ([langchain.com](https://www.langchain.com/blog/reusable-langsmith-evaluator-templates)).

### 3.12 Voice chatbots
Pipeline de tres etapas, cada una con métricas propias:

| Componente | Métrica principal | Complementarias |
|-----------|------------------|----------------|
| STT/ASR | Word Error Rate (WER) | CER, entity accuracy, RTF |
| LLM | Las de texto habituales | Tool accuracy |
| TTS | PESQ, POLQA, ViSQOL, preferencia humana ELO | Prosodia, latencia |

Además: **latencia end-to-end <500ms**, manejo de interrupciones, turn-taking, barge-in ([hamming.ai](https://hamming.ai/blog/the-ultimate-guide-to-asr-stt-tts-for-voice-agents), [sipfront.com](https://sipfront.com/blog/2025/07/how-to-test-ai-voice-bots-comprehensive-guide/), [braintrust.dev](https://www.braintrust.dev/articles/how-to-evaluate-voice-agents)). Botium Speech Processing integra TTS/STT para reusar libraries históricas de IVR como datasets de prueba ([botium-docs.readthedocs.io](https://botium-docs.readthedocs.io/en/latest/03_testing/01_testing_conversational_ai.html)).

### 3.13 Multilingüe
Datasets por idioma con hablantes nativos, tests segmentados por idioma/acento, y validación de code-switching (p.ej. Hindi-English) ([braintrust.dev](https://www.braintrust.dev/articles/how-to-evaluate-voice-agents)).

---

## Laboratorios relacionados

| Módulo | Descripción |
|--------|-------------|
| [01-primer-eval](../modules/01-primer-eval/) | Testing funcional: AnswerRelevancy y Faithfulness básicos |
| [04-multi-turn](../modules/04-multi-turn/) | Context retention y testing de conversaciones multi-turno |
| [05-prompt-regression](../modules/05-prompt-regression/) | Regression testing de prompts: Promptfoo matrices |
| [06-hallucination-lab](../modules/06-hallucination-lab/) | Detección de alucinaciones y groundedness |
| [10-agent-testing](../modules/10-agent-testing/) | ToolCallAccuracy y trajectory evaluation para agentes |
| [11-playwright-streaming](../modules/11-playwright-streaming/) | Testing E2E de UIs con streaming |
