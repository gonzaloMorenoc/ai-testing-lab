# Plataformas comerciales

> Parte del [Manual de Testing de Chatbots y LLMs](./manual-completo.md).

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

## Laboratorios relacionados

| Módulo | Descripción |
|--------|-------------|
| [12-observability](../modules/12-observability/) | Langfuse self-host (alternativa OSS a las plataformas comerciales) |
| [13-drift-monitoring](../modules/13-drift-monitoring/) | Monitoring online con herramientas OSS |
