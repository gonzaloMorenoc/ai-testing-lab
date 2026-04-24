# Buenas prácticas

> Parte del [Manual de Testing de Chatbots y LLMs](./manual-completo.md).

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

## Laboratorios relacionados

| Módulo | Descripción |
|--------|-------------|
| [01-primer-eval](../modules/01-primer-eval/) | Tests deterministas primero: schema + regex antes de LLM-as-judge |
| [05-prompt-regression](../modules/05-prompt-regression/) | Versionado de prompts y baseline por commit |
| [13-drift-monitoring](../modules/13-drift-monitoring/) | Drift detection en producción: PSI/KS sobre embeddings |
