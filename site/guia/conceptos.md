---
title: "Conceptos clave"
description: "Glosario operativo de los términos canónicos del Manual QA AI v13. Cada entrada con definición operativa y referencia al capítulo o módulo donde se desarrolla."
---

# Conceptos clave

Glosario operativo alineado con el Cap. 33 del Manual QA AI v13. La convención editorial sigue el §4.7 del manual: los términos canónicos de la industria se mantienen en inglés (faithfulness, robustness, drift, jailbreak, retrieval, embedding) y se complementan con la traducción al español cuando aporta.

::: tip Cómo se usa
Este glosario es operativo: cada entrada explica para qué sirve el término en QA. Para definiciones canónicas vinculantes, consulta el Cap. 33 del manual. Para uso en código, ver la [tabla maestra de umbrales](./umbrales) y los módulos enlazados.
:::

## Métricas de evaluación

**Faithfulness** — Consistencia entre la respuesta y el contexto recuperado. Una respuesta fiel no introduce información ausente en el contexto. **Distinto de factual accuracy** (§7.3): una respuesta puede tener `faithfulness = 1.0` y ser objetivamente incorrecta si el contexto está desactualizado. Cap. 7, §7.3.

**Answer Relevancy** — Pertinencia de la respuesta respecto al input del usuario. Mide si la respuesta aborda lo preguntado, independientemente de su corrección. En versiones recientes de RAGAS aparece como `Response Relevancy`. §7.1, §7.4.

**Answer Correctness** — Corrección factual de la respuesta frente a un ground truth anotado. Requiere GT explícito. Es la métrica más directa de calidad factual real. §7.1, §7.4.

**Context Precision** — Proporción de chunks recuperados que son relevantes, ponderada por ranking. Métrica del retriever, no del generador. §7.1.

**Context Recall** — Cobertura del contexto recuperado respecto a la respuesta ideal. Complementaria a context precision. §7.1.

**Groundedness** — Sinónimo de faithfulness en algunos frameworks (TruLens). Mantenido por compatibilidad. Cap. 33.

**BERTScore** — Métrica de similitud semántica basada en embeddings BERT alineados por F1. §11.2.

**Cosine similarity** — Producto escalar de embeddings normalizados. Rango teórico `[-1, 1]`; rango habitual con sentence-transformers normalizados sobre texto natural: `[0, 1]`. §11.2.

**NDCG@k** — Normalized Discounted Cumulative Gain. Mide si los documentos relevantes aparecen en las primeras k posiciones del ranking, con penalización por posición. Valor máximo 1.0. §19.3.

**MRR@k** — Mean Reciprocal Rank. Posición media del primer documento relevante en los k resultados. §19.3.

**MAP@k** — Mean Average Precision sobre los k primeros. Considera todos los documentos relevantes, no solo el primero. §19.3.

**Consistency score (robustness)** — Similitud semántica media entre las respuestas a una query original y sus versiones perturbadas. Cap. 12.

## Tabla 4.2 y gates

**Δ (delta)** — Variación de una métrica respecto a la baseline (versión anterior). Cap. 33, [Tabla 4.2](./umbrales).

**Quality gate** — Umbral mínimo que debe superarse en CI/CD para promocionar un cambio. Cap. 18.

**Tabla maestra de umbrales** — La [Tabla 4.2](./umbrales) del manual: única fuente de verdad de los gates del repo. Vive en [`qa_thresholds.py`](https://github.com/gonzaloMorenoc/ai-testing-lab/blob/main/qa_thresholds.py).

**RiskLevel** — Tres niveles de exigencia: `MINIMUM` (red line absoluto), `TARGET` (gate de PR), `HIGH_RISK` (dominios regulados). §4.3.

## LLM-as-Judge y sesgos

**LLM-as-Judge** — Uso de un LLM como evaluador automático de la salida de otro LLM. Permite escalar la evaluación a miles de ejemplos sin anotadores humanos, a costa de heredar sesgos del juez. Cap. 8.

**G-Eval** — Framework de evaluación con cadena de razonamiento explícita. Flexible pero sensible a sesgos sin calibración. §8.3, Liu et al. 2023.

**DAG Metric** — Métrica definida como grafo acíclico de condiciones booleanas. Permite lógica compuesta sin depender de un LLM juez. Determinista. §8.

**Verbosity bias** — Tendencia del LLM juez a preferir respuestas más largas independientemente de su calidad. §8.2.

**Position bias** — Tendencia del juez a preferir la primera opción en comparaciones pairwise. Mitigación: rotar orden y promediar. §8.2.

**Self-enhancement bias** — Cuando el modelo evaluador es el mismo que el generador, tiende a sobrevalorar sus propias respuestas. Mitigación: evaluador distinto al generador. §8.2.

**Lenient bias** — Tendencia a puntuar generosamente sin criterio claro. Mitigación: few-shot calibrado con ejemplos negativos. §8.2.

## Golden datasets y anotación humana

**Golden dataset** — Conjunto de ejemplos anotados por expertos del dominio con respuestas esperadas validadas. Base para evaluación offline y regression testing. Cap. 9.

**Ground truth (GT)** — Respuesta de referencia anotada por experto. Requerida para `Context Recall` y `Answer Correctness`. §7.1, §9.3.

**Inter-annotator agreement (IAA)** — Concordancia entre anotadores humanos. Cap. 31.

**κ de Cohen** — Coeficiente de IAA para dos anotadores con etiquetas categóricas. Umbrales: `≥ 0.61` sustancial, `≥ 0.81` casi perfecto (Landis & Koch). §31.2.

**Krippendorff α** — IAA para N anotadores y cualquier escala. Umbral mínimo aceptable: `≥ 0.667`. Para datasets críticos exigir `≥ 0.80`. §31.2.

**Synthetic data** — Datos generados con LLMs para ampliar golden sets en bootstrap. Útil pero no para evaluación final; introduce sesgo del modelo generador. §9.4.

## Seguridad y OWASP

**OWASP LLM Top 10** — Estándar de las 10 vulnerabilidades de seguridad más críticas en aplicaciones LLM (edición 2025). Cap. 14.

**Prompt Injection (LLM01)** — Manipulación del input para alterar el comportamiento del LLM, superando instrucciones del sistema. §15.1.

**Jailbreak** — Ataque que rompe restricciones de seguridad del modelo. Subtipo de prompt injection orientado a comportamiento. §15.1.

**Indirect prompt injection** — Variante donde las instrucciones maliciosas vienen ocultas en documentos, páginas web o resultados de tools que el modelo procesa como datos. §15.1.

**System Prompt Leakage (LLM07)** — Exposición del system prompt mediante técnicas de extracción. Detectable con canary tokens. §28.3.

**Sensitive Information Disclosure (LLM02)** — Revelación de datos confidenciales del entrenamiento, system prompt o contexto. Cap. 14, Cap. 28.

**Excessive Agency (LLM06)** — Agente con más permisos de los necesarios; puede ejecutar acciones no autorizadas. Mitigación: `permission_boundary`, allowlist de tools, `human_approval_required`. §21.6.

**Improper Output Handling (LLM05)** — Uso sin validación del output del LLM como código, SQL o HTML, permitiendo inyección downstream. Cap. 14.

**Misinformation (LLM09)** — Desinformación generada con tono autoritativo. Mitigación: faithfulness + answer correctness. Cap. 14.

**Unbounded Consumption (LLM10)** — Consumo no controlado de tokens/API calls que puede causar DoS o costes excesivos. Cap. 14, Cap. 27.

**Supply Chain (LLM03)** — Dependencias comprometidas: modelos, datasets de fine-tuning, librerías con backdoors. Cap. 14.

**Data and Model Poisoning (LLM04)** — Manipulación de los datos de entrenamiento o del corpus RAG para alterar el comportamiento. §14.3.

**Vector and Embedding Weaknesses (LLM08)** — Manipulación del vector store para sesgar el retrieval. Cap. 14.

## Robustness y perturbaciones

**Robustness** — Estabilidad de la respuesta ante perturbaciones controladas del input. Cap. 12.

**Hit rate** — Porcentaje de attack prompts que consiguieron una respuesta comprometida. Modelo seguro: hit rate → 0. Cap. 7.

**Refusal rate** — Proporción de prompts maliciosos correctamente rechazados. Umbral objetivo `≥ 0.95`. §25.4.

**False refusal rate** — Proporción de queries legítimas erróneamente rechazadas. Umbral objetivo `≤ 0.05`. Un sistema que rechaza todo tiene `refusal_rate=1.0` pero es inoperable. §25.4.

## Alucinaciones

**Hallucination** — Generación de información falsa o no soportada por el contexto. Cap. 17.

**Intrinsic hallucination** — La respuesta contradice el contexto proporcionado. §17.1.

**Extrinsic hallucination** — La respuesta añade información no presente ni soportada por el contexto (puede ser cierta o falsa). §17.1.

**Temporal hallucination** — Confundir secuencias, inventar fechas, asumir conocimiento desactualizado como vigente. §17.1.

## Drift y monitorización

**Drift (deriva)** — Desplazamiento gradual de la distribución de respuestas del sistema. Cap. 13.

**Query-side drift (covariate shift)** — Cambio en la distribución de inputs. §13.1.

**Response-side drift (concept drift)** — Cambio en cómo el sistema responde a los mismos inputs. §13.1.

**Knowledge drift** — Envejecimiento del corpus indexado frente a la realidad externa. §13.1.

**PSI (Population Stability Index)** — Métrica estadística que mide cambio de distribución entre baseline y período actual. PSI > 0.2 indica cambio significativo. Cap. 13.

**KS test (Kolmogorov-Smirnov)** — Test no paramétrico para detectar diferencia de distribuciones. Usado en drift detection. §13.3.

**Semantic drift** — Sinónimo de drift en contextos semánticos. Cap. 13.

**Centroid shift** — Distancia coseno entre centroides de embeddings (baseline vs actual). §14.3 (módulo 14 del repo).

**AlertHistory** — Registro de resultados de una regla de alerta. Permite detectar tendencias: degrading, recovering, stable. (Módulo 13 del repo.)

**Shadow traffic** — Tráfico real replicado a un sistema candidato sin afectar al usuario final. Usado en pre-deploy. §18.2.

**Canary deployment** — Despliegue progresivo a un porcentaje bajo de tráfico antes del rollout completo. §18.2.

## Observabilidad

**Trace schema** — Contrato mínimo de campos que cada request debe persistir para reproducibilidad y debugging. §19.2.

**Span** — Unidad de trazabilidad en OpenTelemetry. Una llamada LLM, una búsqueda en retriever o una invocación de tool. Cap. 19.

**Execution trace** — Secuencia observable de acciones, decisiones y rationales de un agente. **Sustituye al término obsoleto "reasoning trace"** del v10. §21.4.

**Latencia P50 / P95 / P99** — Percentiles de latencia total request → response. Umbral típico: P95 ≤ 2 s chat, ≤ 5 s RAG. §27.2.

**Time-to-first-token (TTFT)** — Latencia hasta el primer token devuelto. Crítico para UX de streaming. Umbral: ≤ 1 s. §27.2.

## Cost-aware QA

**Cost-aware QA** — Tratamiento del coste por query como métrica de QA de primer orden, con sus propios gates. Cap. 27. (Módulo 15 del repo.)

**Tool fan-out** — Número de tool calls por query en agentes. Cap. 27.

**Cost regression testing** — Verifica que un PR no aumenta el coste medio por query más allá de un umbral. Cap. 27.

## Retrieval y RAG

**RAG** — Retrieval-Augmented Generation: arquitectura retriever + LLM. Cap. 6.

**Vector store** — Base de datos especializada en búsqueda por similitud. §6.1.

**Chunking** — División de documentos en fragmentos para indexación. §6.2, Cap. 29.

**Embedding** — Representación vectorial densa de texto. §6.1.

**Reranker** — Modelo cross-encoder que reordena los top-k del retriever. §6.1, §29.2.

**Information Retrieval (IR) metrics** — Familia de métricas de retrieval: MRR, NDCG, MAP. §19.3.

**HyDE (Hypothetical Document Embeddings)** — Genera respuesta hipotética con LLM y la usa para retrieval (Gao et al. 2022). §29.2. (Módulo 16 del repo.)

**Hybrid search** — Combina BM25 (keyword) con embeddings densos. §29.2.

**Query rewriting** — Reformula la query del usuario antes del retrieval, típicamente con un LLM. §29.2.

**Multi-query retrieval** — Genera N variaciones de la query y une los resultados. §29.2.

**Self-RAG** — El LLM decide cuándo recuperar y reflexiona sobre el resultado (Asai et al. 2023). §29.2.

**Parent-child chunks** — Indexa chunks pequeños, devuelve el contexto extendido (parent). §29.2.

**Sentence-window retrieval** — Indexa oraciones, devuelve la oración +/- N de contexto. §29.2.

## Agentes y function calling

**Function calling / tool use** — Capacidad del LLM de invocar funciones externas con argumentos estructurados. Cap. 30.

**JSON Schema validation** — Validación de argumentos de tool calls. `jsonschema.validate()` requiere `FormatChecker` explícito para validar `format: email/date-time`. §30.3.

**Permission boundary** — Conjunto de tools y dominios permitidos a un agente. §21.6.

**Plan quality score** — Evaluación LLM-as-Judge del plan generado por un agente vs un plan canónico. §21.3.

**Tool selection accuracy** — % de queries que invocan la tool esperada según golden traces. §21.7.

**Idempotencia** — Invocar la misma operación N veces produce el mismo estado final que invocarla una. Requisito en tools con efectos secundarios. §21.5.

**Reversibilidad** — Existencia de operación de compensación documentada para acciones destructivas. §21.5.

## Privacy y PII

**PII (Personally Identifiable Information)** — Información personal identificable. Cap. 28.

**Canary token** — Token único insertado en system prompt o documentos para detectar leakage. §28.3.

**PII scrubbing** — Anonimización automática de PII en logs y respuestas, típicamente con Microsoft Presidio. §28.4.

## Evaluación estadística

**Bootstrap IC95** — Intervalo de confianza al 95 % por remuestreo (≥ 1000 resamples). Más robusto que el z-test con muestras pequeñas o distribuciones no normales. §13.3.

**Kruskal-Wallis** — Test no paramétrico para detectar diferencia entre grupos demográficos. §25.2.

**Mann-Whitney U / Welch t-test** — Tests para comparación pairwise (no paramétrico / paramétrico con varianzas desiguales). §8.5.

## Herramientas y frameworks

**RAGAS** — Framework de evaluación de RAG con métricas reference-free. Cap. 7.

**DeepEval** — Framework de evaluación pytest-native con 50+ métricas. §20.3.

**TruLens** — Framework de evaluación y observabilidad con feedback loop en producción. §20.2.

**Langfuse** — Plataforma OSS de tracing y evaluación unificada. §20.1.

**Phoenix (Arize)** — Plataforma de observabilidad OSS con OTel y auto-instrumentación. §20.1.

**Garak** — Vulnerability scanner para LLMs de NVIDIA. Cap. 7 (módulo del repo).

**DeepTeam** — Capa de red teaming sobre DeepEval, automatiza OWASP LLM Top 10. §14.4.

**Guardrails AI** — Librería Python para validación de input/output de LLMs. Cap. 9 (módulo del repo).

**NeMo Guardrails** — Sistema de guardrails conversacionales de NVIDIA (Colang DSL). §25.3.

**LlamaGuard** — Modelo Meta para multi-categoría de safety, alineado con OWASP LLM. §25.3.

**Microsoft Presidio** — Librería open-source de detección y anonimización de PII multi-idioma. §28.4.

**ranx** — Librería Python de métricas IR (MRR, NDCG, MAP). §19.3.
