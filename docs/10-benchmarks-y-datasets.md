# Benchmarks, datasets y modelos demo

> Parte del [Manual de Testing de Chatbots y LLMs](./manual-completo.md).

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

## Laboratorios relacionados

| Módulo | Descripción |
|--------|-------------|
| [01-primer-eval](../modules/01-primer-eval/) | Primer golden dataset y uso de cassettes |
| [02-ragas-basics](../modules/02-ragas-basics/) | RAGAS Synthesizer para generar goldens automáticamente |
| [06-hallucination-lab](../modules/06-hallucination-lab/) | Datasets de hallucination (LLM-AggreFact, FaithBench) |
| [07-redteam-garak](../modules/07-redteam-garak/) | Datasets de seguridad (HackAPrompt, DAN collection) |
