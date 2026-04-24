# Tendencias 2025-2026

> Parte del [Manual de Testing de Chatbots y LLMs](./manual-completo.md).

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

## Laboratorios relacionados

| Módulo | Descripción |
|--------|-------------|
| [10-agent-testing](../modules/10-agent-testing/) | Trajectory evaluation y ToolCallAccuracy para agentes |
| [12-observability](../modules/12-observability/) | OTel, tracing multi-agente, online evaluation |
| [13-drift-monitoring](../modules/13-drift-monitoring/) | Drift monitoring y alertas en producción |
