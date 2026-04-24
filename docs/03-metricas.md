# Métricas y evaluación en profundidad

> Parte del [Manual de Testing de Chatbots y LLMs](./manual-completo.md).

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

## Laboratorios relacionados

| Módulo | Descripción |
|--------|-------------|
| [01-primer-eval](../modules/01-primer-eval/) | AnswerRelevancyMetric y FaithfulnessMetric en práctica |
| [02-ragas-basics](../modules/02-ragas-basics/) | Las 9 métricas RAGAS con pipeline RAG real |
| [03-llm-as-judge](../modules/03-llm-as-judge/) | G-Eval, DAG Metric y diseño de rúbricas custom |
| [06-hallucination-lab](../modules/06-hallucination-lab/) | HallucinationMetric y RAG Triad de TruLens |
