# Guía exhaustiva de testing de chatbots y modelos de IA para QA Automation Engineers

> Documento de referencia para un QA con stack Playwright / Robot / Selenium / Karate / Python que ya tiene `llm-eval-lab` y `SmartErrorDebugger`. El objetivo es cerrar el puente entre la disciplina clásica de QA (ISTQB, pirámide de testing, CI/CD) y la realidad no determinista de los sistemas basados en LLM.

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

## 4. Métricas y evaluación en profundidad

### 4.1 RAGAS – las nueve que importan
Framework de referencia para RAG ([docs.ragas.io](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/)):

| Métrica | Qué mide | Rango | Necesita ground truth |
|---------|----------|-------|----------------------|
| **Faithfulness** | Claims de la respuesta soportados por el contexto | 0-1 | No |
| **Answer Relevancy** (`ResponseRelevancy`) | Cómo de pertinente es la respuesta al input | 0-1 | No |
| **Context Precision** | Proporción de chunks recuperados que son relevantes, ponderado por ranking | 0-1 | Sí (o LLM-based sin ref) |
| **Context Recall** | Cobertura del contexto recuperado respecto a la respuesta ideal | 0-1 | Sí |
| **Context Entities Recall** | Igual que recall pero a nivel de entidades | 0-1 | Sí |
| **Answer Semantic Similarity** | Similitud de embedding entre respuesta y ground truth | 0-1 | Sí |
| **Answer Correctness** | Combinación factual + semántica | 0-1 | Sí |
| **Noise Sensitivity** | Robustez ante distractores en el contexto | 0-1 | Sí |
| **Topic Adherence / Agent Goal Accuracy** | Para agentes y multi-turn | 0-1 | Parcial |

Recomendación de interpretación: en producción, >0.8 en faithfulness y answer relevancy se considera sólido; context_recall ~0.5 indica retrieval insuficiente la mitad de las veces ([elastic.co](https://www.elastic.co/search-labs/blog/elasticsearch-ragas-llm-app-evaluation)).

### 4.2 DeepEval – 50+ métricas, pytest-native
Las más usadas ([deepeval.com](https://deepeval.com/docs/evaluation-introduction), [deepeval.com](https://deepeval.com/)):

- **G-Eval**: LLM-as-a-judge con chain-of-thought sobre criterios custom, respaldada por paper. El QA define un `criteria` en lenguaje natural.
- **DAG Metric**: grafo dirigido acíclico de decisiones deterministas. Ideal cuando la evaluación tiene reglas claras ("si contiene X, entonces...").
- **RAG**: Faithfulness, Contextual Recall/Precision/Relevancy, AnswerRelevancy.
- **Conversational**: KnowledgeRetention, ConversationCompleteness, ConversationalRelevancy, RoleAdherence.
- **Safety / robustness**: Hallucination, Toxicity, Bias, PIILeakage, PromptAlignment.
- **Agent**: TaskCompletion, ToolCorrectness.
- **Custom**: cualquier función que herede de `BaseMetric`.

### 4.3 Métricas clásicas NLP
Útiles como *smoke test* y para comparaciones reproducibles:

- **BLEU**: precision de n-gramas; originalmente para traducción. Penaliza variaciones morfológicas. Muy criticado como proxy de calidad en generación libre ([medium.com](https://medium.com/@kbdhunga/nlp-model-evaluation-understanding-bleu-rouge-meteor-and-bertscore-9bad7db71170)).
- **ROUGE** (1, 2, L, Lsum, S): recall de n-gramas y longest common subsequence; estándar en summarization.
- **METEOR**: media armónica precision/recall con sinónimos y stemming. Mejor correlación con humano que BLEU ([plainenglish.io](https://plainenglish.io/blog/evaluating-nlp-models-a-comprehensive-guide-to-rouge-bleu-meteor-and-bertscore-metrics-d0f1b1)).
- **BERTScore**: similitud coseno de embeddings contextuales BERT. Semánticamente mucho más rico que n-gramas.
- **chrF, BLEURT, BARTScore**: alternativas modernas. UniEval unifica todas en un framework QA booleano ([elastic.co](https://www.elastic.co/search-labs/blog/evaluating-rag-metrics)).

Regla práctica: no bases un release en BLEU/ROUGE por sí solos; combínalos con LLM-as-a-judge.

### 4.4 LLM-as-a-judge
Idea: usar un modelo fuerte (GPT-4, Claude Opus) para puntuar salidas. El paper seminal de **MT-Bench y Chatbot Arena** demostró que GPT-4 alcanza >80% de acuerdo con preferencias humanas, al nivel del acuerdo inter-humano ([arxiv.org](https://arxiv.org/abs/2306.05685)). Sesgos documentados y mitigaciones:

- **Position bias**: el juez favorece la respuesta A. Mitigación: evaluar en ambos órdenes.
- **Verbosity bias**: premia respuestas largas. Mitigación: rúbrica explícita.
- **Self-enhancement bias**: un modelo se prefiere a sí mismo.
- **Limited reasoning**: para math/code añadir ejecución.

TruLens publicó prompts optimizados para el RAG Triad que superan a MLflow y Bespoke-MiniCheck-7B en LLM-AggreFact ([snowflake.com](https://www.snowflake.com/en/engineering-blog/benchmarking-LLM-as-a-judge-RAG-triad-metrics/)).

### 4.5 Human evaluation
Sigue siendo el gold standard. Patrones:
- **Likert** 1-5 por dimensión.
- **Pairwise preference** (base del Chatbot Arena ELO).
- **Annotation queues** en LangSmith/Langfuse/Phoenix para que SMEs etiqueten traces de producción.

Objetivo operativo: inter-rater agreement ≥80% antes de confiar en la rúbrica ([docs.ragas.io](https://docs.ragas.io/en/stable/concepts/metrics/overview/)).

### 4.6 Reference-based vs reference-free
- **Reference-based** (context recall, answer correctness, BLEU): precisas pero requieren golden dataset mantenido.
- **Reference-free** (faithfulness, answer relevancy, RAG Triad): escalan a producción sin etiquetado previo.

Estrategia común: reference-based en CI (offline), reference-free en online monitoring.

### 4.7 Online vs offline evaluation
- **Offline**: dataset curado, en CI antes de merge (unit-like).
- **Online**: sampling de traces reales, LLM-as-a-judge en streaming, alertas por drift. Langfuse, LangSmith, Arize Phoenix y Braintrust ofrecen ambos modos ([docs.langchain.com](https://docs.langchain.com/langsmith/evaluation)).

---

## 5. Red teaming, seguridad y OWASP Top 10 LLM 2025

### 5.1 OWASP Top 10 for LLM Applications 2025
Listado oficial ([genai.owasp.org](https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/), [owasp.org](https://owasp.org/www-project-top-10-for-large-language-model-applications/assets/PDF/OWASP-Top-10-for-LLMs-v2025.pdf)):

| ID | Riesgo | Notas clave 2025 |
|----|--------|-----------------|
| LLM01 | Prompt Injection | Incluye directa e indirecta (datos externos). Sigue en #1 |
| LLM02 | Sensitive Information Disclosure | Subió del #6 al #2 |
| LLM03 | Supply Chain | Modelos comprometidos, datasets envenenados |
| LLM04 | Data and Model Poisoning | Ahora cubre pre-training, fine-tuning y embeddings |
| LLM05 | Improper Output Handling | XSS, RCE por salida sin sanitizar |
| LLM06 | Excessive Agency | Autonomía excesiva en agentes |
| LLM07 | System Prompt Leakage | **Nuevo**. "System prompts no son controles de seguridad" |
| LLM08 | Vector and Embedding Weaknesses | **Nuevo**. Ataques específicos a RAG: embedding inversion, poisoning |
| LLM09 | Misinformation | Alucinaciones con impacto |
| LLM10 | Unbounded Consumption | DoS, coste descontrolado |

El mensaje dual importante: **RAG no es una solución de seguridad, es una nueva superficie de ataque**, y **los system prompts no son controles de seguridad auditables** porque el LLM es estocástico ([socfortress.medium.com](https://socfortress.medium.com/owasp-top-10-for-llm-applications-2025-7cbb304aabf0)).

### 5.2 Técnicas de ataque para tu test suite

**Prompt injection directa** – el usuario inyecta instrucciones que sobreescriben el system prompt.
**Prompt injection indirecta** – la instrucción maliciosa vive en un documento/web que el RAG recupera. Mucho más difícil de detectar.
**Jailbreaks** – bypass de safety alignment. Familias típicas:
- **DAN ("Do Anything Now")** y variantes: crean un alter ego sin restricciones. Hay +10 iteraciones documentadas en GitHub ([deepgram.com](https://deepgram.com/learn/llm-jailbreaking), [hiddenlayer.com](https://hiddenlayer.com/innovation-hub/prompt-injection-attacks-on-llms/)).
- **Roleplay / Developer Mode / Grandma exploit**.
- **Adversarial suffixes** (GCG, AutoDAN): sufijos optimizados que parecen aleatorios.
- **Many-shot jailbreaking**: abusa de context windows grandes.
- **Encoding attacks**: Base64, quoted-printable, MIME, leetspeak.
- **Crescendo**: escalada gradual en múltiples turnos.
- **Math/Persuasion converters** (PyRIT): transforma el prompt malicioso en ejercicios matemáticos simbólicos ([breakpoint-labs.com](https://breakpoint-labs.com/ai-red-teaming-playground-labs-setup-and-challenge-1-walkthrough-with-pyrit/)).

**PII / data leakage** – pedir al modelo que revele system prompt, API keys, PII de training data.

### 5.3 Frameworks de red teaming

| Tool | Tipo | Licencia | Fuerte en | Link |
|------|------|----------|-----------|------|
| **Garak** | CLI scanner tipo nmap para LLMs | Apache 2.0 (NVIDIA) | Probes estáticos+adaptativos, DAN, encoding, toxicity | [github.com/NVIDIA/garak](https://github.com/NVIDIA/garak) |
| **PyRIT** | Framework Python (Microsoft) | MIT | Orchestrators, converters, multi-turn Crescendo | [github.com/microsoft/PyRIT](https://github.com/Azure/PyRIT) |
| **DeepTeam** | Capa red team sobre DeepEval | Apache 2.0 | OWASP Top 10 automatizado, RAG/agent | [trydeepteam.com](https://www.trydeepteam.com/docs/frameworks-owasp-top-10-for-llms) |
| **Giskard** | Testing + red teaming | Apache 2.0 | Multi-turn attacks, RAGET, EU AI Act | [giskard.ai](https://www.giskard.ai/) |
| **Promptfoo redteam** | CLI redteam integrado | MIT | Plugins sobre inputs estructurados, scoring | [promptfoo.dev](https://www.promptfoo.dev/docs/releases/) |
| **IBM ART** | Adversarial ML clásico | MIT | Evasión en clasificadores | |
| **Lakera Guard / Mindgard** | Comercial | — | Producción en tiempo real, compliance |

Ejemplo Garak (escanear un modelo HF contra DAN 11.0):
```bash
python3 -m garak --target_type huggingface --target_name gpt2 --probes dan.Dan_11_0
```
Genera un JSONL con cada attempt + detector result y un `hit log` con vulnerabilidades confirmadas ([garak.ai](https://garak.ai/)).

Ejemplo DeepTeam para OWASP Top 10:
```python
from deepteam import red_team
from deepteam.frameworks import OWASPTop10
red_team(model_callback=your_callback, framework=OWASPTop10())
```

### 5.4 Guardrails: NeMo vs Guardrails AI
Dos filosofías distintas pero complementarias ([guardrailsai.com](https://guardrailsai.com/blog/nemoguardrails-integration), [aicoolies.com](https://aicoolies.com/comparisons/guardrails-ai-vs-nemo-guardrails)):

| Aspecto | Guardrails AI | NeMo Guardrails |
|---------|---------------|-----------------|
| Enfoque | Validación I/O | Flujo conversacional (Colang) |
| Ecosistema | Python decorators, Guardrails Hub (50+ validators) | LangChain, NVIDIA stack |
| Curva | Baja (Pydantic-like) | Alta (DSL propio) |
| Fuerte en | JSON schema, PII, toxicity per-call | Topic rails, fact-checking, prevenir drift temático |
| Integración | Decoradores sobre llamadas LLM | Capa wrapping del pipeline |

Se integran entre sí desde 2024: usa NeMo para dialogue, Guardrails AI para validación de outputs concretos.

---

## 6. Frameworks open source – comparación operativa

### 6.1 Tabla comparativa

| Framework | Tipo | Lenguaje | pytest nativo | Tracing | RAG metrics | Red team | Self-host |
|-----------|------|----------|---------------|---------|-------------|----------|-----------|
| **DeepEval** | Evaluation | Python | ✅ | Sí (Confident AI) | ✅ 14+ | ✅ DeepTeam | Local |
| **RAGAS** | RAG eval | Python | Parcial | No (integra Langfuse) | ✅ core | No | Local |
| **Promptfoo** | Eval + red team | JS/TS (CLI) | N/A (tiene GH Action) | Limitado | ✅ | ✅ | Local |
| **Giskard** | Testing + red team | Python | Parcial | Hub comercial | ✅ RAGET | ✅ | Local + Hub |
| **TruLens** | Eval + tracing | Python | No | ✅ OTel | ✅ RAG Triad | No | Local |
| **Phoenix** | Observability + eval | Python | No | ✅ OTel | ✅ | Parcial | ✅ |
| **LangSmith** | Observability + eval | Py/JS | ✅ | ✅ | ✅ templates | Templates | Enterprise tier |
| **Langfuse** | Observability + eval | Py/JS | Via SDK | ✅ OTel | Via RAGAS | No nativo | ✅ OSS |
| **MLflow genai** | Eval + tracking | Python | No | ✅ | ✅ | No | ✅ |
| **LangCheck** | Métricas NLP | Python | Sí | No | Parcial | No | Local |
| **Evidently AI** | ML monitoring + LLM | Python | Parcial | No | ✅ básico | No | ✅ |
| **UpTrain** | Eval | Python | No | Parcial | ✅ | No | ✅ |
| **Guardrails AI** | Output validation | Python | N/A | No | N/A | Parcial | ✅ |
| **NeMo Guardrails** | Dialog control | Python (Colang) | N/A | No | N/A | Parcial | ✅ |

### 6.2 Deep dive: DeepEval (el que mejor encaja con tu perfil)
Motivos por los que es la primera recomendación para un pytest + Python user:

- **`deepeval test run` se comporta como pytest**, con flags -n (parallel), -c (cache), -s (skip on missing param), -v (verbose) ([confident-ai.com](https://www.confident-ai.com/docs/llm-evaluation/unit-testing-cicd)).
- **End-to-end y component-level** (con `@observe`) con los mismos `LLMTestCase`/`ConversationalTestCase`.
- **Synthetic dataset generation** vía `Synthesizer`.
- **Benchmarks nativos**: MMLU, HellaSwag, DROP, TruthfulQA, HumanEval, GSM8K ([deepeval.com](https://deepeval.com/docs/benchmarks-introduction)).
- **50+ métricas** research-backed; G-Eval + DAG cubren casi cualquier caso custom.
- **Red teaming** via DeepTeam con framework=OWASP/MITRE/NIST.

Ejemplo mínimo pytest:
```python
import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
from deepeval.test_case import LLMTestCase
from deepeval.dataset import EvaluationDataset

dataset = EvaluationDataset()
dataset.add_goldens_from_csv_file("tests/goldens.csv", context_col_delimiter=";")

@pytest.mark.parametrize("test_case", dataset.test_cases)
def test_rag_pipeline(test_case: LLMTestCase):
    assert_test(test_case, [
        AnswerRelevancyMetric(threshold=0.7),
        FaithfulnessMetric(threshold=0.8),
    ])
```
Y en CLI: `deepeval test run tests/ -n 4 -c`.

### 6.3 RAGAS – el estándar de facto para RAG
Punto fuerte: métricas *reference-free* como faithfulness correlacionan 95% con anotadores humanos en WikiEval ([redis.io](https://redis.io/blog/get-better-rag-responses-with-ragas/)). API nueva (collections-based):
```python
from ragas.metrics.collections import Faithfulness
from ragas.llms import llm_factory
scorer = Faithfulness(llm=llm_factory("gpt-4o-mini", client=AsyncOpenAI()))
result = await scorer.ascore(user_input=..., response=..., retrieved_contexts=[...])
```
Integración limpia con Langfuse: envías `ragas_scores` como `create_score(trace_id=...)` ([langfuse.com](https://langfuse.com/guides/cookbook/evaluation_of_rag_with_ragas)).

### 6.4 Promptfoo – YAML declarativo y red team
Fuerte especialmente si tu equipo no es 100% Python. Config típica:
```yaml
prompts: [file://prompts/v1.txt, file://prompts/v2.txt]
providers: [openai:gpt-4o-mini, anthropic:claude-3-5-sonnet]
tests:
  - vars: {question: "¿Política de devoluciones?"}
    assert:
      - type: llm-rubric
        value: "Debe mencionar el plazo de 30 días"
      - type: contains-any
        value: ["30 días", "reembolso"]
```
`promptfoo eval` corre la matriz; `promptfoo redteam run` genera ataques automáticamente. Se integra en GitHub Actions con caché para controlar coste ([github.com/promptfoo/promptfoo-action](https://github.com/promptfoo/promptfoo-action)).

### 6.5 Giskard – testing + red teaming para empresa
Automatic scan de vulnerabilidades, RAGET (Retrieval-Augmented Generation Evaluation Toolkit) para auto-generar test cases desde tu knowledge base, y agentes multi-turn autónomos sobre 40+ probes. Bien alineado con EU AI Act ([giskard.ai](https://www.giskard.ai/), [appsecsanta.com](https://appsecsanta.com/giskard)).

### 6.6 TruLens – RAG Triad + OpenTelemetry
Introdujo las tres métricas más usadas en RAG: **context relevance, groundedness, answer relevance** ([trulens.org](https://www.trulens.org/getting_started/core_concepts/rag_triad/)). Ahora 100% OpenTelemetry, con semantic conventions propias. Viene con BEIR loader integrado para benchmarks IR (NDCG, hit rate, recall@k).

### 6.7 Phoenix (Arize, Elastic License 2.0)
100% OTel, auto-instrumentation para OpenAI Agents SDK, Claude Agent SDK, LangGraph, LlamaIndex, DSPy, Vercel AI SDK, Mastra, CrewAI ([github.com/Arize-ai/phoenix](https://github.com/Arize-ai/phoenix)). Probablemente la observabilidad OSS más completa sin commercial lock-in (aparte de Langfuse).

### 6.8 MLflow LLM evaluation
La opción natural si ya usas MLflow para ML clásico. `mlflow.genai.evaluate()` separa del `mlflow.models.evaluate()` legacy. Soporta `question-answering` model_type con métricas predefinidas, LLM-as-a-judge custom via `make_metric` y `genai.scorers.Correctness`/`Guidelines` ([mlflow.org](https://mlflow.org/docs/latest/genai/eval-monitor/)).

### 6.9 Pytest plugins y libraries adicionales
- `pytest-asyncio` para tests async con SDKs modernos.
- `pytest-xdist` para paralelizar calls.
- `hypothesis` para property-based testing de prompts (generar inputs con gramática).
- `pytest-recording` / `vcrpy` para grabar/reproducir respuestas LLM (clave para controlar coste en CI).

---

## 7. Plataformas comerciales

| Plataforma | Sweet spot | Precio de entrada | Self-host |
|-----------|-----------|------------------|-----------|
| **LangSmith** | Stacks LangChain / LangGraph, 30+ evaluator templates reusables | Free 5K traces; $39/user | Sólo Enterprise |
| **Langfuse** | OSS + cloud, precio por unidades, MIT | Free 50K obs/mes | ✅ OSS |
| **Braintrust** | Eval-first, CI/CD deployment blocking, proxy integrado | 1M spans free, $249/mes pro | No OSS |
| **Arize AX + Phoenix** | AX comercial sobre Phoenix OSS | Phoenix gratis | ✅ Phoenix |
| **Weights & Biases Weave** | Teams ya en W&B para ML clásico | Por seat | Enterprise |
| **Humanloop** | Product-led, colaboración no técnica, compliance (SOC2/HIPAA) | Sales | Sí |
| **Patronus AI** | Eval especializada, Lynx hallucination detection | Sales | No |
| **HoneyHive** | Eval + observabilidad foco agentes | Sales | No |
| **Galileo** | Seguridad + protect en runtime | Sales | No |
| **Helicone** | Proxy simple cost + latency, caching | Free tier generoso | ✅ OSS |
| **PromptLayer** | Middleware logging + prompt registry, PMs friendly | Free, $150/mes team | No |
| **Vellum** | Visual low-code workflow, one-click deploy | Sales | Enterprise |
| **LastMile AI** | RAG eval con jueces fine-tuneados | Sales | Parcial |
| **LangWatch** | Evaluación + observabilidad, OTel-first | Free tier | Parcial |

Criterios reales de decisión ([arize.com](https://arize.com/llm-evaluation-platforms-top-frameworks/), [braintrust.dev](https://www.braintrust.dev/articles/best-ai-observability-platforms-2025)):

- **OSS + self-host estricto** → Langfuse o Phoenix.
- **Framework-agnóstico + CI/CD blocking** → Braintrust.
- **Todo en LangChain** → LangSmith.
- **Ya pagan APM / solo métricas cost** → Helicone.
- **PM-friendly sin código** → PromptLayer o Humanloop.
- **Compliance EU / regulatory** → Giskard Hub + Langfuse on-prem.

---

## 8. Testing de chatbots conversacionales clásicos

### 8.1 Botium – "el Selenium de los chatbots"
Open source, con 55+ connectors: Dialogflow, Rasa, Amazon Lex, IBM Watson, Microsoft Bot Framework, web widgets (Selenium-based), REST/gRPC, voz ([botium-docs.readthedocs.io](https://botium-docs.readthedocs.io/), [github.com/codeforequity-at/botium-core](https://github.com/codeforequity-at/botium-core)). Usa **BotiumScript**, un DSL simple:
```
#me
hello bot!
#bot
Hello, humanoid! How can I help you ?
```
Soporta `convo files` (flujo esperado) + `utterances files` (N formas de decir lo mismo) para cubrir la variabilidad en el lenguaje del usuario. **Botium Crawler** auto-descubre flujos haciendo clicks en quick replies y genera tests de regresión. Botium Speech Processing permite probar IVRs voice-first. Ecosistema: **Botium Core**, **CLI**, **Box** (UI enterprise), **Bindings** (integra con Jasmine/Mocha/Jest), **Coach** (métricas NLP continuas).

### 8.2 Rasa Pro test framework
Tres niveles ([rasa.com](https://rasa.com/docs/rasa-pro/nlu-based-assistants/testing-your-assistant/)):
- `rasa data validate` – chequea inconsistencias antes de entrenar.
- `rasa test nlu` – cross-validation de intents/entities, genera confusion matrix + histogramas de confianza ([legacy-docs-oss.rasa.com](https://legacy-docs-oss.rasa.com/docs/rasa/reference/rasa/nlu/test/)).
- `rasa test e2e` – stories YAML con asserts sobre slots, flows, custom actions y `generative_response_is_relevant`.

### 8.3 Otras stacks
- **Dialogflow CX** – test cases propios en consola + API; intégralos en CI con el Python client.
- **Microsoft Bot Framework** – Bot Framework Emulator + `botbuilder-testing` para unit tests.
- **IBM Watson Assistant** – dialog tests nativos + Botium connector.
- **Cyara / Cognigy** – enterprise voice/IVR; Cyara simula miles de llamadas concurrentes, validación end-to-end de SIP + STT + NLU.

### 8.4 BDD para chatbots
Con Robot Framework (que ya usas) o `behave`/`pytest-bdd`, puedes escribir:
```gherkin
Scenario: Usuario consulta devolución
  Given El usuario abre el chat
  When Envía "¿política de devoluciones?"
  Then La respuesta debe contener "30 días"
  And La respuesta debe estar fundamentada en la base de conocimiento
```
Luego el step llama al bot (Botium o API directa) y las aserciones corren métricas DeepEval/RAGAS.

---

## 9. CI/CD integration – patrones concretos

### 9.1 GitHub Action para DeepEval (end-to-end)
```yaml
name: LLM Regression Tests
on: [pull_request, push]
jobs:
  evals:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install -r requirements.txt
      - name: Run DeepEval
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          CONFIDENT_API_KEY: ${{ secrets.CONFIDENT_API_KEY }}
        run: deepeval test run tests/ -n 4 -c
```
Bloquea merges si cae faithfulness debajo del threshold ([deepeval.com](https://deepeval.com/docs/evaluation-unit-testing-in-ci-cd), [confident-ai.com](https://www.confident-ai.com/blog/how-to-evaluate-rag-applications-in-ci-cd-pipelines-with-deepeval)).

### 9.2 Promptfoo action con caché (ahorra $$$ en LLM)
```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.promptfoo/cache
      .promptfoo-cache
    key: ${{ runner.os }}-promptfoo-${{ hashFiles('prompts/**') }}-${{ github.sha }}
- uses: promptfoo/promptfoo-action@v1
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    config: 'promptfooconfig.yaml'
    fail-on-threshold: 80
```
([github.com/promptfoo/promptfoo-action](https://github.com/promptfoo/promptfoo-action)).

### 9.3 Regression detection
Patrón: guardar la métrica baseline por commit en el artifact store (o Confident AI/Langfuse). En el PR, comparar main vs PR y marcar en rojo cualquier dimensión con caída >X%.

### 9.4 Cost management
- **Mock layer**: `vcrpy`/`pytest-recording` graba responses en un cassette la primera vez y reusa.
- **Cached LLM judges**: usa un modelo pequeño (gpt-4o-mini, Haiku) para evaluación, reserva GPT-4/Opus para runs de release.
- **Sampling**: en online eval no evalúes el 100% de traces; un 1-5% aleatorio + 100% de traces marcadas como sospechosas.
- **Deterministic-first**: en CI empieza con asserts deterministas (regex, schema, tool signature). Deja LLM-as-a-judge para un workflow más caro pero menos frecuente.
- **Temperature=0 + seed**: para reducir varianza en tests.

### 9.5 Estrategias de mocking
- **Proveedor mock** que devuelve fixtures JSON por prompt hash.
- **Replay de traces** reales exportados desde Langfuse/Phoenix.
- **LLM local** (Ollama con un modelo pequeño) para tests de humo offline.

---

## 10. Python stack – patrones concretos para tu perfil

Tu `llm-eval-lab` ya combina pytest + pydantic v2 + RAGAS + ChromaDB con Groq/Gemini/Mistral/OpenRouter. Ideas para evolucionarlo:

### 10.1 Arquitectura recomendada
```
llm-eval-lab/
├─ src/
│  ├─ providers/          # Groq, Gemini, Mistral, OpenRouter, Ollama
│  ├─ metrics/            # wrappers RAGAS + DeepEval + custom
│  ├─ datasets/           # golden loaders (JSON, CSV, HF)
│  └─ judges/             # LLM-as-a-judge con prompt templates versionados
├─ tests/
│  ├─ unit/               # prompts, parsers, schemas
│  ├─ component/          # retrievers, chains, tools
│  ├─ e2e/                # flujos completos
│  ├─ security/           # prompt injection, jailbreaks
│  └─ conftest.py         # fixtures: vector store temp, judge fijo, caché
├─ goldens/               # datasets versionados
├─ reports/               # HTML/JSON outputs
└─ .github/workflows/
```

### 10.2 Patrón pydantic v2 para test cases
```python
from pydantic import BaseModel, Field
class RAGGolden(BaseModel):
    input: str
    expected_output: str
    expected_context: list[str]
    metadata: dict = Field(default_factory=dict)
    risk_tier: Literal["low", "medium", "high"] = "medium"
```

### 10.3 LangChain + LlamaIndex testing
- LangSmith: `evaluate(app, data="dataset", evaluators=[correct])` con evaluator que recibe `{inputs, outputs, reference_outputs}` ([blog.langchain.com](https://blog.langchain.com/easier-evaluations-with-langsmith-sdk-v0-2/)).
- LlamaIndex: `BatchEvalRunner` + RAGAS `LlamaIndexWrapper`.

### 10.4 Hugging Face `evaluate`
```python
import evaluate
bleu = evaluate.load("bleu")
bertscore = evaluate.load("bertscore")
```
Útil como baseline deterministic rápido dentro de un test DeepEval custom.

### 10.5 SmartErrorDebugger → ejemplo de testing RAG completo
Tu sistema con BM25 + ChromaDB + BGE-Reranker + DeepSeek-R1:8B vía Ollama se evalúa exactamente en los ejes:
- **Retriever (BM25 + vector)**: Context Precision, Context Recall (dataset con queries + chunks relevantes etiquetados).
- **Reranker (BGE)**: mismo dataset, comparar NDCG@k antes y después del rerank.
- **Generator (DeepSeek-R1)**: Faithfulness + Answer Relevancy + G-Eval custom para "cita fuentes correctamente".
- **Pipeline E2E vía FastAPI**: Playwright contra la Streamlit UI validando streaming + citaciones.
- **Seguridad**: Garak directo al endpoint Ollama, y DeepTeam OWASP contra el /chat FastAPI.

---

## 11. Playwright para UIs de chatbot

### 11.1 Retos específicos
- Respuestas **streaming** (aparecen token a token).
- Contenido **no determinista** – no se puede aserción por texto exacto.
- Widgets **embebidos en iframes** con Shadow DOM.
- **Esperas**: sin timeouts fijos; usa auto-waiting de Playwright.

### 11.2 Patrón recomendado
```python
import re
from playwright.sync_api import Page, expect

def test_password_reset_intent(page: Page):
    page.goto("https://app.example.com/chat")
    page.get_by_role("textbox", name="Mensaje").fill("¿cómo reseteo mi clave?")
    page.get_by_role("button", name="Enviar").click()

    last_bot = page.locator('[data-testid="bot-message"]').last
    # Espera a que termine el streaming
    expect(last_bot).to_have_attribute("data-complete", "true", timeout=30_000)
    text = last_bot.inner_text()

    # Asserts no deterministas: regex + evaluador semántico
    assert re.search(r"(reset|restablec|recuperar)", text, re.IGNORECASE)

    # Delegar la validación semántica a DeepEval (LLM-as-judge)
    from deepeval.metrics import GEval
    from deepeval.test_case import LLMTestCase, LLMTestCaseParams
    metric = GEval(
        name="IntentoCorrecto",
        criteria="La respuesta debe guiar al usuario a resetear su contraseña y no pedir información sensible.",
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.INPUT],
        threshold=0.7,
    )
    metric.measure(LLMTestCase(input="¿cómo reseteo mi clave?", actual_output=text))
    assert metric.is_successful(), metric.reason
```

### 11.3 Streaming bien hecho
Tres estrategias ([medium.com/@gunashekarr11](https://medium.com/@gunashekarr11/testing-ai-chatbots-with-playwright-the-future-nobody-is-ready-for-64495def2c40), [opcito.com](https://www.opcito.com/blogs/using-playwright-for-genai-app-testing)):
1. **Data-attribute flag** (`data-complete="true"`) que la app expone cuando termina la respuesta.
2. **Wait for network idle** del endpoint SSE.
3. **Polling de estabilización**: el texto no cambia en X ms → considerado completo.

### 11.4 Widgets embebidos / iframes
```python
frame = page.frame_locator("iframe[title='Chatbot']")
frame.get_by_role("textbox").fill("...")
```

### 11.5 Asserts sobre contenido dinámico
Combina:
- **Regex / contains** para palabras obligatorias (PII redaction, mencionar marca).
- **Schema validation** si tu bot devuelve JSON estructurado.
- **LLM-as-judge** (delegate) para lo semántico.
- **Screenshot testing** para el layout (no para el texto).

### 11.6 Playwright 1.59 para agentes de QA
Features recientes útiles: `browser.bind()` para compartir browser entre CLI/MCP/tests, `npx playwright trace` CLI para debugging por agentes de código, `page.screencast()` con overlays anotados ([testdino.com](https://testdino.com/blog/playwright-release-guide/)). Ideal si integras Claude Code / Cursor para generar tests automáticamente.

### 11.7 Proyecto de referencia
Hay un repo `bot-test-playwright` con suites ya organizadas en RAGAS compliance, security (prompt injection), retrieval/performance, multi-turn y UX ([github.com/dkoul/bot-test-playwright](https://github.com/dkoul/bot-test-playwright)). Útil como plantilla.

---

## 12. Benchmarks y datasets

### 12.1 Benchmarks estándar
| Benchmark | Qué mide | Formato | Estado 2026 |
|-----------|----------|---------|------------|
| **MMLU** (15k preguntas, 57 temas) | Conocimiento general multitask | MCQ (5-shot) | Saturado en frontier (>90%) |
| **MMLU-Pro** | Versión endurecida (10 opciones) | MCQ | Referencia actual |
| **HellaSwag** | Commonsense completion | MCQ | Saturado |
| **TruthfulQA** (817) | Veracidad frente a misconceptions | Free-form + MC | Vigente |
| **HumanEval** (164) | Code gen Python, unit tests | pass@k | Saturado |
| **HumanEval+, MBPP+** | Versiones con 35-80x más tests | pass@k | Vigente |
| **SWE-Bench Verified** | Resolución real de issues GitHub | % resolved | Vigente, muy difícil |
| **GSM8K** | Matemáticas grade-school | Exact match | Saturado |
| **GPQA-Diamond** | Reasoning PhD-level (bio/quím/fís) | MCQ | Vigente, diferencia top models |
| **ARC-Challenge** | Ciencias grade-school | MCQ | Vigente |
| **BIG-Bench Hard** | Razonamiento complejo | Varias | Vigente |
| **HELM** (Stanford) | Multi-dim (accuracy, calibration, bias, tox) | Holistic | Vigente para compliance |
| **GAIA** | Agentes real-world con tool use | End-to-end | Vigente |
| **MT-Bench** (80 multi-turn) | Conversación y follow-up | GPT-4 judge | Referencia de facto |
| **Chatbot Arena** | Preferencia humana crowdsourced | ELO | Referencia #1 |

Fuentes: [confident-ai.com](https://www.confident-ai.com/blog/llm-benchmarks-mmlu-hellaswag-and-beyond), [lxt.ai](https://www.lxt.ai/blog/llm-benchmarks/), [ibm.com](https://www.ibm.com/think/topics/llm-benchmarks), [evidentlyai.com](https://www.evidentlyai.com/llm-guide/llm-benchmarks).

### 12.2 RAG y retrieval
- **BEIR** – 18 datasets heterogéneos de retrieval. TruLens expone `TruBEIRDataLoader` en 3 líneas ([trulens.org](https://www.trulens.org/getting_started/quickstarts/groundtruth_evals_for_retrieval_systems/)).
- **MS MARCO** – passage + document ranking.
- **HotpotQA, NQ, TriviaQA** – QA con contexto.
- **LLM-AggreFact** – 11k claims etiquetados para groundedness.
- **CELLS / FaithBench** – datasets de plain-language summarization para perturbaciones.

### 12.3 Datasets de seguridad / red team
- **HackAPrompt** – 600k+ prompts maliciosos etiquetados.
- **DAN prompts collection** en GitHub ([langgptai/LLM-Jailbreaks](https://github.com/langgptai/LLM-Jailbreaks)).
- **RealToxicityPrompts** – toxicity benchmark clásico.
- **Gandalf levels** (Lakera) – challenges escalonados, excelente para practicar ([lakera.ai](https://www.lakera.ai/blog/direct-prompt-injections)).
- **AI Village CTF** (DEF CON).

### 12.4 Ejecutar benchmarks desde código
DeepEval wrap directo ([deepeval.com](https://deepeval.com/docs/benchmarks-mmlu)):
```python
from deepeval.benchmarks import MMLU
from deepeval.benchmarks.tasks import MMLUTask
bench = MMLU(tasks=[MMLUTask.HIGH_SCHOOL_COMPUTER_SCIENCE], n_shots=3)
bench.evaluate(model=your_custom_llm)
print(bench.overall_score)
```
O lm-eval-harness (más bajo nivel):
```bash
lm_eval --model hf --model_args pretrained=mistralai/Mistral-7B \
        --tasks mmlu,hellaswag,arc_challenge --num_fewshot 5
```

### 12.5 Crear tu propio golden dataset
Receta condensada ([getmaxim.ai](https://www.getmaxim.ai/articles/building-a-golden-dataset-for-ai-evaluation-a-step-by-step-guide/), [sigma.ai](https://sigma.ai/golden-datasets/), [innodata.com](https://innodata.com/what-are-golden-datasets-in-ai/)):

1. **Sourcing** – 80% casos reales de producción + 20% sintéticos con RAGAS `Synthesizer` o DeepEval `Synthesizer`.
2. **Cobertura** – happy path, edge cases, adversarial, slices por demografía/idioma.
3. **Tamaño** – fórmula práctica: ~246 muestras por slice para 80% pass rate con ±5% a 95% confianza.
4. **Anotación** – 2 SMEs por ejemplo + tercer desempate; medir inter-rater agreement (≥80%).
5. **Metadata rica** – risk tier, dominio, idioma, fecha, prompt version, golden version.
6. **Versionado** – Git LFS o DVC; ata versión de golden a versión de prompt.
7. **Decontamination** – chequea que no haya overlap con datos de training (especial crítico si fine-tuneas).
8. **Refresh ciclo** – inyecta failures de producción como nuevos casos (drift management).
9. **Governance** – alinea con NIST AI RMF e ISO/IEC 42001 para audit trail.

Para RAG, el workflow "silver → golden" de Microsoft + RAGAS `TestsetGenerator` acelera mucho el bootstrap ([medium.com](https://medium.com/data-science-at-microsoft/the-path-to-a-golden-dataset-or-how-to-evaluate-your-rag-045e23d1f13f)).

---

## 13. Chatbots y modelos demo para practicar

### 13.1 Públicos gratis
- **Hugging Face Spaces** – catálogo masivo; ejemplos: `Qwen/Qwen3-Demo` (streaming, multi-turn), `course-demos/Chatbot-Demo` (básico para smoke test) ([huggingface.co/spaces](https://huggingface.co/spaces)).
- **Lakera Gandalf** – levels de prompt injection; perfecto para entrenar jailbreaks.
- **Chatbot Arena** (`lmarena.ai`) – compara modelos anónimos.
- **OpenAssistant, HuggingChat**.

### 13.2 Local (recomendado para CI reproducible)
- **Ollama** con `llama3.2`, `mistral`, `deepseek-r1:8b`, `qwen2.5` – lo que ya usas en SmartErrorDebugger.
- **LocalAI** – drop-in OpenAI-compatible.
- **LM Studio** – GUI.
- **text-generation-webui**.

### 13.3 APIs con free tier
- **Groq** (fast inference gratis, limits generosos).
- **Google Gemini API** free tier.
- **Mistral La Plateforme** tier free.
- **OpenRouter** con modelos gratuitos (`:free` suffix).
- **Together AI** créditos iniciales.

### 13.4 Chatbots demo para testing funcional
- **Rasa demo bots** en `RasaHQ/rasa-demo` (chatbot de soporte Sara).
- **Microsoft Bot Framework samples** repo (multiples Dialogs, LUIS, QnA).
- **Dialogflow CX prebuilt agents** (airport, banking, travel).
- **Botium samples** (Facebook, Dialogflow, Watson connectors) ([github.com/pdesgarets/testmybot](https://github.com/pdesgarets/testmybot)).
- **Microsoft AI Red Teaming Playground Labs** – 13 retos tipo CTF con notebooks PyRIT pre-armados ([github.com/microsoft/AI-Red-Teaming-Playground-Labs](https://github.com/microsoft/AI-Red-Teaming-Playground-Labs)).

### 13.5 Datasets listos para evaluación
- **SQuAD 2.0** – QA extractivo.
- **MS MARCO** – retrieval.
- **SAMSum, DialogSum** – resumen de diálogos.
- **MultiWOZ** – dialog state tracking multi-dominio.
- **PersonaChat** – conversaciones consistentes de personaje.
- **Kaggle**: "Amazon Reviews Q&A", "Customer Support on Twitter", "Movie Dialog Corpus".

---

## 14. Buenas prácticas

### 14.1 Pirámide + tres grandes niveles de confianza
1. **Tests deterministas rápidos y baratos** (schema, regex, tool signature, cost guard).
2. **Evaluadores referenciales** (RAGAS context recall, BLEU para regresión específica).
3. **LLM-as-a-judge + human review** en releases y online.

### 14.2 Manejo del no determinismo
- Temperature=0 + seed en tests reproducibles.
- N=3-5 ejecuciones, mide media y p95.
- Thresholds con margen (`>= 0.7` no `== 1.0`).
- Define **slices** y monitorea cada uno, no solo el promedio global.

### 14.3 Versionado de prompts y modelos
Trata cada prompt como código: archivo versionado, ID semántico, link bidireccional con test run. DeepEval `Prompt` + hyperparameters log, LangSmith Prompt Hub, PromptLayer, Langfuse Prompt Management lo facilitan ([deepeval.com](https://deepeval.com/docs/evaluation-prompts)).

### 14.4 Continuous evaluation en producción
- Sampling (1-5%) + 100% de traces con error/baja confianza.
- LLM-as-judge asíncrono (no bloquea al usuario).
- Dashboards con quality, cost, latency por dimensión.
- Alertas por drift (caída en faithfulness > X%).

### 14.5 Drift detection
- **Input drift**: distribución de longitudes, idioma, categorías de intent.
- **Output drift**: distribución de scores de evaluadores; PSI/KS sobre embeddings.
- **Concept drift**: ground truth cambia (p.ej. política de devoluciones cambió).
Evidently AI y Arize Phoenix lo hacen out-of-the-box.

### 14.6 Presupuesto y coste
- Judge model ≠ production model (usa uno más barato).
- Cache determinístico por `hash(prompt+input)`.
- `pytest -k smoke` en cada PR, suite completa solo nightly.
- Marca tests `@pytest.mark.expensive` y filtra en CI.

### 14.7 Observabilidad
OpenTelemetry como capa común: TruLens, Phoenix, Langfuse y LangSmith hablan OTel. Esto permite migrar entre plataformas sin rewrite ([langfuse.com](https://langfuse.com/docs)).

---

## 15. Tendencias 2025-2026

### 15.1 Agentic AI testing
Los agentes autónomos (OpenAI Agents SDK, LangGraph, CrewAI, AutoGen) requieren evaluar **trajectorias**, no solo outputs. Las métricas clave:
- **ToolCallAccuracy / F1** (RAGAS).
- **Agent Goal Accuracy**.
- **Trajectory evaluation** – comparar secuencia de steps contra un "gold trajectory".
- **Coverage audits** (SafeAudit paper): detectar patrones inseguros que benchmarks estándar no cubren ([arxiv.org](https://arxiv.org/pdf/2603.18245)).
- **Proxy State-Based Evaluation** (PayPal AI): evaluar agentes sin backends deterministas ([arxiv.org](https://arxiv.org/pdf/2602.16246)).

### 15.2 Multi-agent system testing
Testing de orquestadores (supervisor-worker, debate, consensus). Métricas emergentes: hand-off correctness, deadlock detection, cost compounding. LangGraph tracing + LangSmith templates específicos lideran este frente.

### 15.3 RAG con reranking
Evaluar tres capas: retriever, reranker, generator. Métricas: NDCG@k antes/después de rerank + context precision. TruLens BEIR loader + Phoenix RAG analysis son el stack actual.

### 15.4 Voice AI testing
Explosión en 2025. Herramientas dedicadas: Hamming, Sipfront, Cekura, futureagi. Benchmarks TTS ahora están en **Artificial Analysis Speech Arena** con ELO preference ([inworld.ai](https://inworld.ai/resources/best-voice-ai-tts-apis-for-real-time-voice-agents-2026-benchmarks)). Para STT: WER multi-accent + entity accuracy en medical/legal/financial.

### 15.5 Reasoning models (DeepSeek-R1, o3, Claude "Extended thinking")
Evaluación especializada: chain-of-thought validity, "thought leakage" (el modelo reveló reasoning privado), eficiencia de tokens de thinking. TruLens y DeepEval han añadido `ReasoningValidity` custom metrics.

### 15.6 Agentic red teaming continuo
Giskard Hub, Lakera y NeuralTrust ofrecen red teaming continuo: cada vez que cambias tu base de conocimiento, re-genera ataques y los ejecuta. Esperable que en 2026 sea baseline igual que SAST/DAST en AppSec.

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