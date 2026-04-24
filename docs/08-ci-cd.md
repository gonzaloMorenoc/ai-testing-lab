# CI/CD integration y Python stack

> Parte del [Manual de Testing de Chatbots y LLMs](./manual-completo.md).

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

## Laboratorios relacionados

| Módulo | Descripción |
|--------|-------------|
| [01-primer-eval](../modules/01-primer-eval/) | CI con DeepEval + cassettes VCR (sin API keys) |
| [05-prompt-regression](../modules/05-prompt-regression/) | Promptfoo en GitHub Actions con caché |
| [07-redteam-garak](../modules/07-redteam-garak/) | Red team nightly (workflow redteam-nightly.yml) |
