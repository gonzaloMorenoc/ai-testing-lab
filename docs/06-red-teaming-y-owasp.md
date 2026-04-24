# Red teaming, seguridad y OWASP Top 10 LLM 2025

> Parte del [Manual de Testing de Chatbots y LLMs](./manual-completo.md).

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

## Laboratorios relacionados

| Módulo | Descripción |
|--------|-------------|
| [07-redteam-garak](../modules/07-redteam-garak/) | Garak CLI: probes DAN, encoding, toxicity |
| [08-redteam-deepteam](../modules/08-redteam-deepteam/) | DeepTeam: OWASP Top 10 LLM automatizado |
| [09-guardrails](../modules/09-guardrails/) | NeMo Guardrails y Guardrails AI: validación de I/O |
| [demos/vulnerable-bot](../demos/vulnerable-bot/) | Target CTF intencional para practicar ataques |
