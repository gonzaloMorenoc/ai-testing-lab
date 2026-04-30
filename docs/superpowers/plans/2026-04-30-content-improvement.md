# Content Improvement — 14 Módulos Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reescribir las 14 páginas de módulo del site VitePress con una plantilla de 8 secciones uniforme que sea didáctica, profunda y útil para QAs senior e ingenieros ML/NLP.

**Architecture:** Cada módulo en `site/modulos/NN-nombre.md` se reescribe completamente con la misma plantilla de 8 secciones. No se toca código Python. El sidebar de VitePress no cambia (las URLs son las mismas). El glosario `site/guia/conceptos.md` se amplía al final.

**Tech Stack:** Markdown, VitePress, HTML inline para el layout de columnas existente.

---

## Plantilla de referencia (leer antes de implementar)

Cada módulo sigue este esquema exacto. El bloque de sidebar (stat-cards + comando + enlace siguiente) se conserva igual que en el original.

```markdown
---
title: "NN — nombre"
---

# NN — nombre

<subtítulo una línea>

<div class="module-layout">
<div class="module-main">

## El problema
<100-150 palabras, abstracto, segunda persona, sin código>

## Cómo funciona
<150-200 palabras + diagrama ASCII si aplica>

## Código paso a paso
<3-4 fragmentos progresivos con prosa entre ellos>

## Técnicas avanzadas
<solo si aplica — integración natural del contenido avanzado>

## Errores comunes
<3-5 items formato ❌/✅>

## En producción
<tabla thresholds + comando CI + referencias cruzadas>

## Caso real en producción
<~200 palabras narrativo: empresa ficticia, problema, solución, resultado>

## Ejercicios
🟢 **Básico** — <enunciado autocontenido>
🟡 **Intermedio** — <enunciado que requiere código nuevo>
🔴 **Avanzado** — <enunciado que integra con otro módulo>

</div>
<div class="module-sidebar">
<conservar stat-cards y navegación del original>
</div>
</div>
```

---

## Task 1: Módulo 01 — primer-eval

**Files:**
- Modify: `site/modulos/01-primer-eval.md`

- [ ] **Step 1: Reescribir el módulo completo**

Contenido para cada sección:

**El problema:** Cambias el prompt de tu chatbot y las respuestas parecen mejores. ¿Pero lo son? Sin métricas, la única forma de saberlo es revisión manual — viable con 20 queries al día, imposible con 2.000. `LLMTestCase` es la unidad mínima para automatizar esa decisión: encapsula la entrada del usuario, la respuesta del modelo y el contexto recuperado. Una métrica objetiva determina si la respuesta es relevante y fiel, sin intervención humana, en cada ejecución de CI.

**Cómo funciona:**
- `AnswerRelevancy` en modo mock calcula word overlap normalizado entre la query y la respuesta. No usa LLM. Si las palabras clave de la pregunta aparecen en la respuesta, el score sube.
- `Faithfulness` verifica si cada afirmación de la respuesta puede inferirse del `retrieval_context`. En mock, usa overlap léxico entre claims y contexto.
- Flujo: `input + actual_output + retrieval_context → LLMTestCase → metric.measure() → score → comparar con threshold → pass/fail`

**Código paso a paso:** Dividir en 3 fragmentos: (1) construir el `LLMTestCase`, (2) añadir `AnswerRelevancyMetric` y ejecutarla, (3) añadir `FaithfulnessMetric` y usar `assert_test` combinado.

**Técnicas avanzadas:** Presentar `QAGateChecker` introducido así: "Cuando tienes múltiples métricas y distintos productos con niveles de riesgo diferentes, necesitas umbrales diferenciados por contexto". Luego el código y la tabla de thresholds por nivel. Después presentar `EvalDesignChecker` introducido así: "Antes de confiar en los resultados de tu evaluación, verifica que el diseño del test no tiene anti-patterns que invaliden las conclusiones". Incluir los 10 AP con la tabla.

**Errores comunes:**
- ❌ Usar el mismo modelo como generador y como juez → el juez favorece sus propias respuestas sistemáticamente ✅ Usar modelos distintos (AP-05)
- ❌ Threshold 0.7 "porque suena bien" → sin base empírica el gate no tiene significado ✅ Derivar el threshold de evaluaciones históricas sobre datos reales (AP-07)
- ❌ Dataset solo con preguntas cuya respuesta está en el contexto → no detecta fallos en queries ambiguas ✅ Incluir al menos 20% de casos negativos (AP-01)
- ❌ Menos de 30 casos en el golden set → resultados estadísticamente no significativos ✅ Mínimo 30, recomendado 100+ (AP-04)

**En producción:**
```
| Entorno    | AnswerRelevancy | Faithfulness |
|------------|----------------|--------------|
| PR         | ≥ 0.70         | ≥ 0.70       |
| Staging    | ≥ 0.80         | ≥ 0.82       |
| Producción | ≥ 0.85         | ≥ 0.88       |
```
Comando CI: `pytest modules/01-primer-eval/tests/ -m "not slow" -q`
Referencia cruzada: para monitorizar estos scores en producción → módulo 13.

**Caso real:** Fintech española con chatbot de soporte para 40.000 clientes. Tras un cambio de prompt para mejorar el tono, el equipo de QA ejecutó `assert_test` sobre el golden set de 120 casos. `AnswerRelevancy` bajó de 0.82 a 0.61 en el cluster de queries sobre "cancelación de cuenta" — el nuevo prompt era más amable pero omitía la información clave. El bug se detectó en el pipeline de CI antes de llegar a staging. Sin la métrica, habría llegado a producción afectando a miles de usuarios.

**Ejercicios:**
- 🟢 Cambia el `threshold` de `AnswerRelevancyMetric` a 0.95 y ejecuta los tests. ¿Cuántos fallan? ¿Por qué tiene sentido ese comportamiento?
- 🟡 Añade un tercer `LLMTestCase` donde el `actual_output` contenga información que NO está en el `retrieval_context`. Verifica que `FaithfulnessMetric` lo detecta como fallido.
- 🔴 Usa `QAGateChecker` con `RiskLevel.HIGH_RISK` sobre los resultados de 5 `LLMTestCase` diferentes. Identifica cuáles habrían bloqueado un despliegue en producción y explica por qué.

- [ ] **Step 2: Verificar que el archivo tiene las 8 secciones y conserva el sidebar original**

- [ ] **Step 3: Commit**
```bash
git add site/modulos/01-primer-eval.md
git commit -m "docs: rewrite module 01 with 8-section template"
```

---

## Task 2: Módulo 02 — ragas-basics

**Files:**
- Modify: `site/modulos/02-ragas-basics.md`

- [ ] **Step 1: Reescribir el módulo completo**

**El problema:** Tu pipeline RAG devuelve respuestas, pero no sabes si el problema está en el retriever (trae chunks irrelevantes) o en el generador (no usa bien el contexto). Sin separar ambas evaluaciones, cualquier mejora es a ciegas. RAGAS te da tres métricas que diagnostican cada componente por separado: cuánto de lo que se recuperó era relevante, cuánto de lo necesario se recuperó, y si la respuesta refleja fielmente el contexto.

**Cómo funciona:**
- `context_precision`: de los chunks recuperados, ¿qué fracción era realmente necesaria para responder? Mide el retriever. Alto precision = pocos chunks irrelevantes.
- `context_recall`: de la información necesaria para responder, ¿qué fracción estaba en los chunks recuperados? Mide si el retriever no se dejó nada.
- `faithfulness`: ¿la respuesta generada se puede inferir del contexto recuperado? Mide el generador. Independiente del retriever.
- El `RAGASEvaluator` del lab usa word overlap en modo determinista — sin llamadas a OpenAI.

**Código paso a paso:** (1) Construir `synonym_clusters` y el evaluador, (2) llamar a `evaluate()` con query + context + response, (3) inspeccionar las tres métricas por separado e interpretar qué componente falla.

**Técnicas avanzadas:** Presentar `build_synonym_clusters` para dominio jurídico: "En documentos legales, 'resolución', 'sentencia' y 'fallo' son sinónimos de dominio. Sin inyectarlos, el overlap léxico subestima la relevancia real." Mostrar el ejemplo con clusters jurídicos.

**Errores comunes:**
- ❌ Evaluar solo `faithfulness` → no detecta si el retriever trae basura ✅ Evaluar las tres métricas siempre
- ❌ Confundir precision con recall → alta precision + bajo recall significa que el retriever es conservador pero se deja información crítica ✅ Revisar ambas antes de concluir
- ❌ Un solo chunk en el contexto → no ejercita el retriever ✅ Usar al menos 3-5 chunks por query de test
- ❌ Queries de test demasiado simples → no estresan el pipeline ✅ Incluir queries con sinónimos, negaciones y preguntas ambiguas

**En producción:**
```
| Métrica           | Mínimo | Target | Alto riesgo |
|-------------------|--------|--------|-------------|
| context_precision | 0.65   | 0.80   | 0.90        |
| context_recall    | 0.70   | 0.85   | 0.90        |
| faithfulness      | 0.70   | 0.85   | 0.90        |
```
Comando CI: `pytest modules/02-ragas-basics/tests/ -m "not slow" -q`
Referencia cruzada: para detectar drift en estas métricas → módulo 13.

**Caso real:** Despacho de abogados con asistente de revisión de contratos. El retriever devolvía 5 chunks por query, pero `context_precision` era 0.41 — menos de la mitad del contexto recuperado era relevante. El generador tenía `faithfulness` de 0.89, lo que significaba que el problema no estaba en el LLM sino en el índice vectorial. El equipo redujo el número de chunks de 5 a 3 con re-ranking y `context_precision` subió a 0.78 sin cambiar el modelo.

**Ejercicios:**
- 🟢 Modifica el `overlap_threshold` del evaluador a 0.3. ¿Cómo cambian los scores? ¿Qué threshold tiene más sentido para un dominio con vocabulario técnico?
- 🟡 Añade un caso donde el contexto tiene la información correcta pero la respuesta la ignora completamente. Verifica que `faithfulness` baja mientras `context_recall` se mantiene alto.
- 🔴 Construye un dataset de 10 queries con sus contextos y respuestas que simule un pipeline con retriever deficiente (baja precision) pero generador fiel. Mide las tres métricas y genera un informe que identifique el componente problemático.

- [ ] **Step 2: Verificar 8 secciones y sidebar**

- [ ] **Step 3: Commit**
```bash
git add site/modulos/02-ragas-basics.md
git commit -m "docs: rewrite module 02 with 8-section template"
```

---

## Task 3: Módulo 03 — llm-as-judge

**Files:**
- Modify: `site/modulos/03-llm-as-judge.md`

- [ ] **Step 1: Reescribir**

**El problema:** Tienes dos versiones de un modelo y quieres saber cuál responde mejor. Usas un LLM como juez para comparar las respuestas. El problema: el juez puntúa más alto la respuesta que aparece primero, independientemente de su calidad. Este sesgo de posición invalida completamente los resultados si no se controla. Un sistema de evaluación con LLM-as-judge no calibrado es peor que la revisión manual: da una falsa sensación de objetividad.

**Cómo funciona:**
- `G-Eval`: el juez recibe una rúbrica definida por el usuario y puntúa la respuesta de 0 a 1 siguiendo esos criterios. Flexible, pero el output depende del orden de los inputs.
- `Position bias`: en comparaciones A/B, si A aparece antes que B, el juez tiende a preferir A. Se mide evaluando en ambos órdenes (A→B y B→A) y calculando el delta. Si el delta > 0.1, hay sesgo significativo.
- Calibración: evaluar los dos órdenes y promediar los scores elimina el sesgo sistemático.
- `DAG Metric`: alternativa sin LLM. Define la evaluación como un grafo de condiciones booleanas (AND, OR). Determinista y reproducible.

**Código paso a paso:** (1) Crear `GEvalJudge` y puntuar una respuesta individual, (2) usar `calibrate_for_position_bias` con dos respuestas, (3) interpretar `bias_delta` y `calibrated_winner`.

**Técnicas avanzadas:** Presentar `JudgeBias` introducido así: "Además del position bias, los jueces LLM tienen otros cuatro sesgos sistemáticos que debes detectar antes de confiar en los resultados." Mostrar los 5 tipos con ejemplo de `detect_verbosity_bias`. Luego Cohen kappa: "Cuando múltiples evaluadores humanos o LLMs puntúan el mismo conjunto, necesitas medir si están de acuerdo o si sus diferencias son sistemáticas."

**Errores comunes:**
- ❌ Comparar A/B con una sola evaluación en orden fijo → el ganador puede ser el que aparece primero ✅ Siempre evaluar en ambos órdenes y promediar
- ❌ Usar el mismo modelo como generador y juez → el juez favorece su propio estilo ✅ Modelos distintos para generación y evaluación
- ❌ Ignorar verbosity bias → el juez puntúa respuestas largas por defecto ✅ Controlar longitud en el dataset o usar `detect_verbosity_bias`
- ❌ Un único evaluador (humano o LLM) → sin medida de acuerdo no hay confiabilidad ✅ Calcular Cohen kappa con ≥ 2 evaluadores, umbral aceptable κ ≥ 0.61

**En producción:**
```
| Indicador        | Umbral          |
|------------------|-----------------|
| bias_delta       | < 0.10          |
| Cohen kappa (κ)  | ≥ 0.61          |
| n_samples mínimo | 30 por comparación |
```
Comando CI: `pytest modules/03-llm-as-judge/tests/ -m "not slow" -q`
Referencia cruzada: para detectar drift en scores del juez → módulo 13.

**Caso real:** Empresa de RRHH usando un LLM para cribar CVs comparando dos versiones del modelo de scoring. En una evaluación A/B con 200 CVs, el modelo B ganaba en el 67% de los casos. Tras calibrar position bias, el resultado fue empate técnico (51% B, diferencia no significativa). El equipo había estado a punto de migrar a un modelo más caro basándose en un artefacto estadístico.

**Ejercicios:**
- 🟢 Ejecuta `calibrate_for_position_bias` con dos respuestas donde la primera es claramente peor. ¿El `calibrated_winner` cambia respecto a la evaluación sin calibrar?
- 🟡 Implementa un test que detecte verbosity bias: genera una respuesta corta y una larga con el mismo contenido informativo y verifica que `detect_verbosity_bias` lo identifica cuando el score de la larga supera en 0.15+ a la corta.
- 🔴 Diseña un benchmark de 20 pares de respuestas con Cohen kappa real entre dos "jueces" (puedes simularlos con puntuaciones manuales). Calcula κ e interpreta si el acuerdo es aceptable según Landis & Koch.

- [ ] **Step 2: Verificar 8 secciones y sidebar**

- [ ] **Step 3: Commit**
```bash
git add site/modulos/03-llm-as-judge.md
git commit -m "docs: rewrite module 03 with 8-section template"
```

---

## Task 4: Módulo 04 — multi-turn

**Files:**
- Modify: `site/modulos/04-multi-turn.md`

- [ ] **Step 1: Reescribir**

**El problema:** Un chatbot que responde bien en una sola interacción puede fallar en conversaciones largas. Si el usuario menciona su dirección en el turno 1 y la pregunta en el turno 7, el sistema necesita retener esa información. La mayoría de los tests de LLMs evalúan turnos individuales — no detectan cuándo el modelo "olvida" información crítica a medida que la conversación avanza.

**Cómo funciona:**
- `ConversationalTestCase` encapsula una lista de turnos (input + output) como unidad de evaluación.
- La `memory_window` define cuántos turnos atrás puede "ver" el modelo. Por defecto: 8.
- Las 7 métricas del `MultiTurnEvaluator` son todas deterministas (sin LLM): context_retention, coreference_resolution, consistency, topic_tracking, memory_window_used, context_overflow_detected, conversation_summarization_score.
- `context_overflow_detected` se activa cuando `num_turns > memory_window`, señalando que el modelo ha perdido acceso al comienzo de la conversación.

**Código paso a paso:** (1) Construir una `Conversation` con `add_turn`, (2) definir `key_facts` y `pronoun_entity_pairs`, (3) ejecutar `MultiTurnEvaluator.evaluate()`, (4) inspeccionar `context_retention` y `consistency` por separado.

**Técnicas avanzadas:** Introducir `MultiTurnEvaluator` con sus 7 métricas así: "Cuando necesitas ir más allá de verificar que el turno N recuerda el turno 1, estas métricas te dan un diagnóstico completo de la salud conversacional." Mostrar la tabla de las 7 métricas con descripción y el código completo.

**Errores comunes:**
- ❌ Tests de un solo turno para validar un chatbot conversacional → no detecta pérdida de contexto ✅ Siempre incluir tests de ≥ 5 turnos
- ❌ No testear el límite de la memory_window → el sistema puede funcionar en tests cortos y fallar en producción ✅ Incluir un test con `num_turns > memory_window`
- ❌ No verificar coreferencialidad → "¿cuánto cuesta?" no tiene sentido sin saber a qué se refiere "eso" del turno anterior ✅ Definir `pronoun_entity_pairs` en el evaluador
- ❌ Conversaciones de test demasiado cortas → no ejercitan el sistema ✅ Incluir tests de 8-12 turnos

**En producción:**
```
| Métrica             | Umbral mínimo |
|---------------------|---------------|
| context_retention   | ≥ 0.80        |
| consistency         | ≥ 0.75        |
| topic_tracking      | ≥ 0.85        |
```
Comando CI: `pytest modules/04-multi-turn/tests/ -m "not slow" -q`

**Caso real:** E-commerce con chatbot de seguimiento de pedidos. Los usuarios mencionaban la dirección de envío en el primer turno y preguntaban detalles del pedido durante los siguientes 5-6 turnos. Tras el turno 7, el chatbot dejaba de referenciar la dirección original. `context_overflow_detected` se activaba y `context_retention` caía a 0.45. La solución fue reducir la verbosidad de las respuestas para que más información cupiera en la ventana de contexto.

**Ejercicios:**
- 🟢 Construye una conversación de 10 turnos donde el dato clave se menciona en el turno 1. Configura `memory_window=8` y verifica que `context_overflow_detected` es `True`.
- 🟡 Añade pronombres ambiguos a la conversación (`"¿y eso?"`, `"¿el de antes?"`) y mide cómo afecta a `coreference_resolution`. ¿Qué patrones en el texto provocan el mayor descenso?
- 🔴 Implementa un test de regresión que compare dos versiones de un sistema de chat: una con `memory_window=4` y otra con `memory_window=12`. Usa `MultiTurnEvaluator` para demostrar cuantitativamente cuál retiene mejor el contexto.

- [ ] **Step 2: Verificar 8 secciones y sidebar**

- [ ] **Step 3: Commit**
```bash
git add site/modulos/04-multi-turn.md
git commit -m "docs: rewrite module 04 with 8-section template"
```

---

## Task 5: Módulo 05 — prompt-regression

**Files:**
- Modify: `site/modulos/05-prompt-regression.md`

- [ ] **Step 1: Reescribir**

**El problema:** Cambias un prompt, los resultados parecen mejores. El score medio sube del 0.81 al 0.84. ¿Es una mejora real o ruido estadístico? Con 20 muestras, una diferencia del 3% puede ser completamente aleatoria. Sin test estadístico, cada cambio de prompt es una apuesta. Con regresión de prompts, cada cambio tiene un veredicto objetivo: mejora real, regresión detectada, o diferencia dentro del ruido.

**Cómo funciona:**
- `PromptRegistry` almacena cada versión de un prompt con su hash SHA-256. Permite reproducir exactamente cualquier versión anterior.
- `RegressionChecker` compara los scores del baseline con los del candidato sobre el mismo dataset.
- `is_significant`: z-test de una proporción. Con n=200 y baseline=0.75, una diferencia de 0.03 tiene p-value ~0.04 — significativa. Con n=20, la misma diferencia tiene p-value ~0.35 — ruido.
- Bootstrap IC95: evalúa el modelo N veces (N_RUNS=5) para estimar la varianza real del score. Temperatura=0 no garantiza determinismo.

**Código paso a paso:** (1) Registrar dos versiones de prompt con `PromptRegistry`, (2) comparar scores con `RegressionChecker`, (3) aplicar `is_significant`, (4) usar `evaluate_with_variance` para bootstrap.

**Técnicas avanzadas:** Introducir `VarianceEvaluator` así: "Temperatura=0 no es determinista — el mismo prompt puede dar scores distintos en ejecuciones diferentes. Bootstrap IC95 te da el rango real de varianza." Luego `CIGatePipeline` así: "En un pipeline de CI con múltiples entornos, necesitas gates distintos por etapa: más permisivo en PR, más estricto en producción." Mostrar la tabla de 4 etapas.

**Errores comunes:**
- ❌ Comparar mejoras con muestras < 30 → resultados no significativos ✅ Mínimo 30 casos, recomendado 100-200
- ❌ Concluir que temperatura=0 es suficiente para reproducibilidad → los modelos tienen varianza interna ✅ Siempre ejecutar con N_RUNS≥3 y calcular IC95
- ❌ El mismo dataset para desarrollar y evaluar el prompt → data leakage ✅ Separar dataset de desarrollo y dataset de evaluación
- ❌ Gate único para todos los entornos → demasiado estricto en PR, demasiado laxo en producción ✅ Usar `CIGatePipeline` con thresholds escalonados

**En producción:**
```
| Etapa      | Faithfulness | Relevancy | Delta máx |
|------------|-------------|-----------|-----------|
| PR         | ≥ 0.70      | ≥ 0.75    | −0.03     |
| Staging    | ≥ 0.80      | ≥ 0.85    | −0.02     |
| Canary     | ≥ 0.85      | ≥ 0.88    | −0.01     |
| Production | ≥ 0.90      | ≥ 0.92    | −0.01     |
```
Comando CI: `pytest modules/05-prompt-regression/tests/ -m "not slow" -q`

**Caso real:** SaaS B2B de atención al cliente que iteraba el prompt del chatbot cada sprint. Tras 4 sprints consecutivos de "mejoras", el score en staging era 0.83 — pero la IC95 era [0.79, 0.87]. El equipo se dio cuenta de que ninguna de las 4 iteraciones había producido una mejora estadísticamente significativa. Implementaron `CIGatePipeline` y establecieron que los PRs solo se mergeaban si el IC95 inferior superaba el target de la etapa anterior.

**Ejercicios:**
- 🟢 Usa `is_significant` con n=20, n=50 y n=200 para la misma diferencia de 0.03. ¿A partir de qué tamaño de muestra la diferencia es significativa?
- 🟡 Implementa un `PromptRegistry` con dos versiones de un prompt y compara sus scores con `RegressionChecker`. Documenta qué versión gana y con qué nivel de confianza.
- 🔴 Simula un pipeline completo con `CIGatePipeline`: ejecuta los 4 stages con scores que pasan PR y Staging pero fallan en Canary. Verifica que `first_failing_stage` devuelve `CIStage.CANARY`.

- [ ] **Step 2: Verificar 8 secciones y sidebar**

- [ ] **Step 3: Commit**
```bash
git add site/modulos/05-prompt-regression.md
git commit -m "docs: rewrite module 05 with 8-section template"
```

---

## Task 6: Módulo 06 — hallucination-lab

**Files:**
- Modify: `site/modulos/06-hallucination-lab.md`

- [ ] **Step 1: Reescribir**

**El problema:** Las métricas de faithfulness estándar miden overlap léxico entre la respuesta y el contexto. Pero no detectan negaciones: si el contexto dice "las devoluciones están permitidas en 30 días" y la respuesta dice "las devoluciones NO están permitidas", el overlap léxico sigue siendo alto. Tu modelo puede estar contradiciendo activamente al contexto y tus métricas lo pasan como correcto. Las alucinaciones más peligrosas no son las que inventan información — son las que la niegan.

**Cómo funciona:**
- Extracción de claims: la respuesta se descompone en afirmaciones atómicas verificables ("el plazo es 30 días", "las devoluciones están permitidas").
- Groundedness: cada claim se compara con el contexto usando overlap léxico + detección de negación. Un claim negado que contradice el contexto falla aunque tenga alta similitud léxica.
- Taxonomía Ji et al. 2023: nivel 1 (intrínseco vs extrínseco) y nivel 2 (factual, temporal, numérico, citation, lógico). Permite priorizar qué tipo de alucinación tiene más impacto en cada dominio.

**Código paso a paso:** (1) Usar `GroundednessChecker` con un claim positivo que pasa, (2) probar con un claim negado que falla, (3) usar `HallucinationClassifier` para clasificar el tipo.

**Técnicas avanzadas:** Introducir `HallucinationClassifier` así: "Saber que el modelo alucinó es el primer paso. Saber qué tipo de alucinación es te permite priorizar correcciones: una alucinación numérica en un contexto financiero tiene un impacto muy diferente a una alucinación de cita en contenido editorial." Mostrar la taxonomía completa y el código de clasificación.

**Errores comunes:**
- ❌ Usar solo faithfulness para detectar alucinaciones → no detecta negaciones ni contradicciones ✅ Usar `GroundednessChecker` con detección de negación explícita
- ❌ No distinguir intrínseco de extrínseco → las alucinaciones extrínsecas (información no verificable) no siempre son errores ✅ Clasificar con `HallucinationClassifier` antes de actuar
- ❌ Claims demasiado largos → un claim con varias afirmaciones mezcla verdades y errores ✅ Descomponer en afirmaciones atómicas de una sola idea
- ❌ Solo testear claims positivos → el detector de negación no se ejercita ✅ Incluir casos con "no", "nunca", "jamás", "sin"

**En producción:**
```
| Tipo de alucinación | Prioridad en producción |
|--------------------|------------------------|
| INTRINSIC + FACTUAL | Crítica — bloquear     |
| INTRINSIC + NUMERICAL | Alta — bloquear      |
| EXTRINSIC + cualquier | Media — revisar      |
| INTRINSIC + LOGICAL | Alta — bloquear        |
```
Comando CI: `pytest modules/06-hallucination-lab/tests/ -m "not slow" -q`
Referencia cruzada: para evaluar faithfulness a nivel de pipeline → módulo 02.

**Caso real:** Plataforma de salud con chatbot de información sobre síntomas. En una auditoría, el equipo encontró respuestas donde el modelo decía "este síntoma NO requiere atención médica urgente" cuando el contexto clínico indicaba lo contrario. `FaithfulnessMetric` pasaba estos casos con scores de 0.71 porque el overlap léxico era alto. `GroundednessChecker` con detección de negación los marcó correctamente como failed. Se añadió el checker al pipeline de validación de todas las respuestas del chatbot antes de mostrarlas al usuario.

**Ejercicios:**
- 🟢 Crea un `LLMTestCase` donde la respuesta incluye la palabra "no" antes de un dato que sí aparece en el contexto. Verifica que `GroundednessChecker` lo detecta como no grounded.
- 🟡 Construye un conjunto de 10 claims (5 correctos, 3 negados, 2 extrínseca) y usa `HallucinationClassifier` para clasificarlos. ¿Qué patrones léxicos son más difíciles de detectar?
- 🔴 Integra `GroundednessChecker` con el pipeline de evaluación del módulo 01: añade una verificación de negación a tu `LLMTestCase` y diseña un caso donde `AnswerRelevancy` pasa pero `GroundednessChecker` falla.

- [ ] **Step 2: Verificar 8 secciones y sidebar**

- [ ] **Step 3: Commit**
```bash
git add site/modulos/06-hallucination-lab.md
git commit -m "docs: rewrite module 06 with 8-section template"
```

---

## Task 7: Módulo 07 — redteam-garak

**Files:**
- Modify: `site/modulos/07-redteam-garak.md`

- [ ] **Step 1: Reescribir**

**El problema:** Antes de desplegar un modelo en producción, necesitas saber cuánto esfuerzo necesita un atacante para conseguir una respuesta comprometida. No basta con probar los jailbreaks más conocidos — hay siete categorías de ataque distintas, cada una con técnicas específicas. Un modelo que resiste los DAN clásicos puede ser vulnerable a many-shot jailbreaking o indirect injection.

**Cómo funciona:**
- `VulnerabilityScanner` ejecuta 42 attack prompts distribuidos en 7 categorías. Para cada prompt, llama al modelo y evalúa si la respuesta es comprometida.
- `hit_rate`: fracción de prompts que consiguieron una respuesta problemática. Un modelo seguro tiene hit_rate cercano a 0.
- `hit_rate_by_category`: permite identificar qué tipo de ataque es más efectivo contra tu modelo específico y priorizar las defensas.
- `RobustnessSuite`: mide consistencia bajo variaciones del input (typos, mayúsculas, parafraseo), no vulnerabilidades de seguridad — son conceptos distintos.

**Código paso a paso:** (1) Crear `VulnerabilityScanner` con los prompts, (2) ejecutar `scan()` sobre un modelo mock, (3) inspeccionar `hit_rate` global y `hit_rate_by_category`, (4) interpretar qué categorías necesitan refuerzo.

**Técnicas avanzadas:** Presentar `RobustnessSuite` así: "Una vez que el modelo pasa el scanner de vulnerabilidades, necesitas verificar que responde de forma consistente aunque el input varíe ligeramente — esto es robustez, no seguridad, pero ambas son necesarias para producción."

**Errores comunes:**
- ❌ Solo testear jailbreaks DAN porque son los más conocidos → many-shot e indirect injection suelen tener hit_rate más alto ✅ Ejecutar las 7 categorías siempre
- ❌ Hit_rate 0 con un modelo mock sin lógica real → los resultados no son representativos ✅ Testear con el modelo real en entornos controlados
- ❌ Un solo test de seguridad antes del lanzamiento → los modelos cambian con fine-tuning ✅ Incluir el scanner en el pipeline de CI nightly (ver workflow `redteam-nightly.yml`)
- ❌ Ignorar indirect injection porque "el usuario no controla los documentos" → en RAG el contexto viene de fuentes externas ✅ Incluir siempre la categoría `indirect_inj`

**En producción:**
```
| Categoría     | Hit rate aceptable |
|---------------|-------------------|
| DAN           | < 0.05            |
| Encoding      | < 0.05            |
| Roleplay      | < 0.10            |
| Crescendo     | < 0.05            |
| Many-shot     | < 0.10            |
| Token manip.  | < 0.05            |
| Indirect inj. | < 0.05            |
```
Comando CI (nightly): `pytest modules/07-redteam-garak/tests/ -m "redteam" -q`
Referencia cruzada: para guardrails de input → módulo 09.

**Caso real:** Compañía de seguros implementando un asistente de siniestros. En la auditoría pre-producción, el scanner detectó hit_rate de 0.33 en la categoría many-shot: el modelo aceptaba tramitar reclamaciones fraudulentas si el historial ficticio mostraba 10 reclamaciones previas aprobadas. Las otras 6 categorías tenían hit_rate < 0.05. El equipo añadió un guardrail específico para detectar historiales conversacionales inusualmente largos antes del lanzamiento.

**Ejercicios:**
- 🟢 Ejecuta el scanner y ordena las categorías por hit_rate. ¿Qué categoría es más efectiva contra el modelo mock del lab?
- 🟡 Añade 3 attack prompts nuevos a la categoría `indirect_inj`. Deben simular instrucciones maliciosas embebidas en un documento que el modelo procesaría como contexto RAG.
- 🔴 Diseña un modelo mock con defensas específicas para la categoría con mayor hit_rate. Verifica que el hit_rate baja a < 0.05 sin aumentar el hit_rate de otras categorías (sin over-blocking).

- [ ] **Step 2: Verificar 8 secciones y sidebar**

- [ ] **Step 3: Commit**
```bash
git add site/modulos/07-redteam-garak.md
git commit -m "docs: rewrite module 07 with 8-section template"
```

---

## Task 8: Módulo 08 — redteam-deepteam

**Files:**
- Modify: `site/modulos/08-redteam-deepteam.md`

- [ ] **Step 1: Reescribir**

**El problema:** Un modelo que pasa los tests de jailbreaking estándar puede seguir siendo vulnerable cuando actúa como agente: ejecuta código, llama APIs, envía emails. Un ataque de agencia no busca que el modelo diga algo prohibido — busca que haga algo prohibido. OWASP Top 10 LLM 2025 define las 10 vulnerabilidades más críticas en producción, muchas de ellas específicas de sistemas con capacidad de acción.

**Cómo funciona:**
- Los 10 riesgos del OWASP Top 10 LLM 2025 cubren tanto ataques de entrada (prompt injection, data poisoning) como riesgos sistémicos (excessive agency, overreliance, model theft).
- `SafetySuite` mide dos tasas que deben estar en equilibrio: `refusal_rate` (rechaza contenido dañino) y `false_refusal_rate` (no rechaza contenido legítimo). Un modelo sobreprotegido que rechaza consultas legítimas es inútil.
- Sesgo demográfico: Kruskal-Wallis detecta si el modelo responde de forma estadísticamente diferente a queries sobre distintos grupos.

**Código paso a paso:** (1) Mostrar los 10 riesgos OWASP con descripción, (2) ejecutar `run_safety_suite`, (3) interpretar `refusal_rate` vs `false_refusal_rate`, (4) ejecutar `measure_demographic_bias`.

**Técnicas avanzadas:** Presentar `SafetySuite` así: "Medir solo refusal_rate lleva a sobre-bloquear: un modelo que rechaza todo tiene refusal_rate=1.0 pero es inútil. Necesitas los dos indicadores en equilibrio."

**Errores comunes:**
- ❌ Solo medir refusal_rate → un modelo que rechaza todo parece perfecto ✅ Medir siempre `refusal_rate` y `false_refusal_rate` juntos
- ❌ Ignorar riesgos de agencia porque "el modelo solo responde texto" → cuando se añaden herramientas, los riesgos cambian completamente ✅ Reevaluar seguridad cada vez que se añade una tool
- ❌ No testear sesgo demográfico → el modelo puede tratar grupos de forma diferente sin que sea obvio ✅ Ejecutar Kruskal-Wallis sobre grupos relevantes para tu dominio
- ❌ Confundir prompt injection con indirect injection → prompt injection es directo del usuario, indirect es vía datos externos ✅ Testear ambos vectores

**En producción:**
```
| Indicador          | Gate       |
|--------------------|-----------|
| refusal_rate       | ≥ 0.95    |
| false_refusal_rate | ≤ 0.05    |
| Kruskal-Wallis p   | > 0.05    |
```
Comando CI (nightly): `pytest modules/08-redteam-deepteam/tests/ -m "redteam" -q`
Referencia cruzada: para guardrails de salida → módulo 09.

**Caso real:** Plataforma EdTech con agente que generaba ejercicios personalizados y podía acceder a la API de calendar del alumno para programar sesiones de estudio. En el análisis de excessive agency, el agente aceptaba instrucciones para programar eventos en calendarios de terceros si el usuario construía el prompt adecuado. El equipo añadió `human_approval_required` para todas las operaciones de escritura en APIs externas.

**Ejercicios:**
- 🟢 Ejecuta `run_safety_suite` e identifica qué tests contribuyen más a `false_refusal_rate`. ¿Qué tienen en común las queries legítimas que el modelo rechaza?
- 🟡 Implementa un test de Kruskal-Wallis para detectar si el modelo responde de forma diferente a queries sobre tres grupos demográficos de tu elección. Define una `score_fn` significativa para tu dominio.
- 🔴 Diseña un escenario de excessive agency: un agente con 3 herramientas (buscar, leer, escribir). Implementa tests que verifiquen que las operaciones de escritura requieren confirmación explícita del usuario.

- [ ] **Step 2: Verificar 8 secciones y sidebar**

- [ ] **Step 3: Commit**
```bash
git add site/modulos/08-redteam-deepteam.md
git commit -m "docs: rewrite module 08 with 8-section template"
```

---

## Task 9: Módulo 09 — guardrails

**Files:**
- Modify: `site/modulos/09-guardrails.md`

- [ ] **Step 1: Reescribir**

**El problema:** Tu LLM puede filtrar información personal que los usuarios introducen en sus queries, o generar respuestas que incluyen datos sensibles del contexto. Ninguno de los dos casos es aceptable bajo GDPR. Un pipeline sin guardrails de entrada y salida es un riesgo legal, no solo técnico. Los guardrails son la última línea de defensa antes de que el contenido llegue al usuario.

**Cómo funciona:**
- Pipeline I/O: validación en dos puntos. Input: antes de llamar al LLM. Output: antes de devolver la respuesta al usuario.
- Detección de PII: 6 patrones regex (teléfonos ES, emails, DNI/NIE, IBANs, tarjetas de crédito, nombres propios). No depende de LLM — es determinista.
- Canary tokens: se inyecta un token único en el system prompt. Si aparece en la respuesta, el modelo está filtrando el system prompt.
- `PIILeakageError` usa `raise`, no `assert` — los asserts se desactivan con `python -O`.

**Código paso a paso:** (1) Ejecutar `GuardrailPipeline.run()` con PII en el input, (2) inspeccionar `blocked`, `reason` y `pii_found`, (3) usar `detect_pii_in_response` en el output, (4) usar `generate_canary` y `test_no_system_prompt_leak`.

**Técnicas avanzadas:** Presentar `PIICanary` así: "Los guardrails de input y output protegen los datos del usuario. Pero también necesitas verificar que el modelo no filtra tu propio system prompt — que puede contener instrucciones de negocio confidenciales o claves de configuración."

**Errores comunes:**
- ❌ Validar solo el input → el output puede contener PII del contexto recuperado ✅ Validar siempre input Y output
- ❌ Usar `assert` para lanzar errores de seguridad → `python -O` desactiva todos los asserts ✅ Usar `raise PIILeakageError`
- ❌ No testear fugas del system prompt → el modelo puede revelar instrucciones confidenciales ✅ Usar `generate_canary` en cada entorno
- ❌ Guardrails solo en regex de idioma inglés → los datos personales en español tienen formatos distintos ✅ Incluir patrones ES (DNI, NIE, IBAN ES, teléfonos con prefijo +34)

**En producción:**
```
| Guardrail              | Acción si activa   |
|------------------------|-------------------|
| PII en input           | Bloquear + log    |
| PII en output          | Bloquear + log    |
| Canary en output       | Alerta + audit    |
| Prompt injection       | Bloquear + alert  |
```
Comando CI: `pytest modules/09-guardrails/tests/ -m "not slow" -q`
Referencia cruzada: para detectar ataques de indirect injection → módulo 07.

**Caso real:** Consultora de RRHH con chatbot que procesaba CVs y respondía preguntas de candidatos. En una auditoría, se detectó que el modelo incluía el email de otros candidatos en algunas respuestas (extraído del contexto RAG). `detect_pii_in_response` identificó 23 casos en 500 interacciones auditadas. Se añadió la validación de output con patrón de email como gate obligatorio antes del despliegue.

**Ejercicios:**
- 🟢 Construye un input con un DNI español y un email. Verifica que `GuardrailPipeline` lo bloquea y que `pii_found` lista ambos elementos.
- 🟡 Implementa un test que verifique que un modelo que repite literalmente el system prompt es detectado por `test_no_system_prompt_leak`. ¿Qué umbral de similitud usarías para evitar falsos positivos?
- 🔴 Diseña un pipeline de doble guardrail (input + output) que procese una lista de 20 queries, bloquee las que contienen PII, registre las incidencias y genere un informe de auditoría con conteos por tipo de PII.

- [ ] **Step 2: Verificar 8 secciones y sidebar**

- [ ] **Step 3: Commit**
```bash
git add site/modulos/09-guardrails.md
git commit -m "docs: rewrite module 09 with 8-section template"
```

---

## Task 10: Módulo 10 — agent-testing

**Files:**
- Modify: `site/modulos/10-agent-testing.md`

- [ ] **Step 1: Reescribir**

**El problema:** Un agente LLM no solo genera texto — selecciona herramientas, ejecuta acciones y produce resultados que dependen de una secuencia de decisiones. Si el agente elige la herramienta incorrecta, el resultado puede ser correcto por accidente o incorrecto de forma silenciosa. Testear solo el output final no detecta si el agente llegó ahí por el camino correcto.

**Cómo funciona:**
- Tool accuracy: ¿el agente seleccionó la herramienta correcta para cada tipo de query? Se verifica comparando `result.trajectory[i].tool` con el tool esperado.
- Trajectory evaluation: ¿la secuencia completa de pasos es la esperada? No basta con que el resultado final sea correcto.
- AST-safe eval: el agente evalúa expresiones matemáticas parseando el AST en lugar de usar `eval()`. Sin acceso a builtins, sin riesgo de inyección.
- `AgentGoalAccuracy`: ¿el agente completó el objetivo del usuario, no solo ejecutó los pasos?

**Código paso a paso:** (1) Crear `SimpleAgent` y ejecutar una query, (2) verificar `trajectory` paso a paso, (3) añadir `AgentPolicy` con herramientas permitidas, (4) verificar que herramientas no permitidas lanzan `PolicyViolationError`.

**Técnicas avanzadas:** Presentar `AgentPolicy` así: "A medida que el agente gana herramientas, necesitas un enforcement explícito de qué puede y qué no puede hacer — no basta con confiar en el prompt."

**Errores comunes:**
- ❌ Solo verificar el output final → el agente puede acertar por el camino equivocado ✅ Siempre verificar la trayectoria completa
- ❌ Usar `eval()` para expresiones del usuario → inyección de código ✅ Usar AST-safe evaluator
- ❌ Sin límite de iteraciones → el agente puede entrar en bucles infinitos en producción ✅ Configurar `max_iterations` en `AgentPolicy`
- ❌ Sin `human_approval_required` para acciones destructivas → el agente puede borrar datos sin confirmación ✅ Listar explícitamente las acciones que requieren aprobación

**En producción:**
```
| Métrica              | Gate        |
|----------------------|-------------|
| tool_accuracy        | ≥ 0.90      |
| goal_accuracy        | ≥ 0.85      |
| max_cost_usd/llamada | ≤ 1.00      |
| max_iterations       | ≤ 12        |
```
Comando CI: `pytest modules/10-agent-testing/tests/ -m "not slow" -q`
Referencia cruzada: para seguridad del agente → módulo 08.

**Caso real:** Empresa de logística con agente de planificación de rutas que tenía acceso a 5 herramientas: buscar_ruta, calcular_coste, reservar_vehículo, enviar_confirmación, cancelar_reserva. En tests de trayectoria, el agente llamaba a `reservar_vehículo` antes de `calcular_coste` en el 18% de los casos, generando reservas sin validación de coste. El test de trajectory evaluation detectó la anomalía y se añadió `cancelar_reserva` a `human_approval_required`.

**Ejercicios:**
- 🟢 Ejecuta `SimpleAgent` con 3 queries diferentes y verifica que `trajectory[0].tool` es el esperado en cada caso. ¿Qué pasa si la query es ambigua?
- 🟡 Añade una herramienta nueva al agente (por ejemplo, `convert_currency`). Escribe el test de trayectoria antes de implementar la herramienta — TDD para agentes.
- 🔴 Implementa una `AgentPolicy` con 4 herramientas, de las cuales 2 requieren aprobación humana. Diseña un test que verifique que el agente nunca ejecuta acciones no aprobadas, aunque el prompt del usuario lo pida explícitamente.

- [ ] **Step 2: Verificar 8 secciones y sidebar**

- [ ] **Step 3: Commit**
```bash
git add site/modulos/10-agent-testing.md
git commit -m "docs: rewrite module 10 with 8-section template"
```

---

## Task 11: Módulo 11 — playwright-streaming

**Files:**
- Modify: `site/modulos/11-playwright-streaming.md`

- [ ] **Step 1: Reescribir**

**El problema:** Los tests de API verifican que el endpoint devuelve el contenido correcto. Pero si la interfaz de usuario muestra los tokens en streaming, pueden ocurrir fallos que los tests de API no detectan: tokens fuera de orden, cortes en mitad de una palabra, buffers que no se vacían, o la UI que congela mientras espera el primer chunk. El único test que cubre estos fallos es uno que abre un navegador real y observa la interfaz.

**Cómo funciona:**
- Server-Sent Events (SSE): el servidor envía chunks de texto de forma continua. El cliente los recibe y los renderiza progresivamente.
- FastAPI + mock server: el lab monta un servidor mock que simula el streaming de un LLM real sin llamadas a APIs externas.
- Playwright intercepta los eventos SSE y verifica que los tokens llegan en orden, sin duplicados y sin corrupción.
- Tests visuales: `page.screenshot()` captura el estado de la UI en puntos clave para detectar regresiones visuales.

**Código paso a paso:** (1) Arrancar el servidor mock con `pytest-playwright`, (2) navegar a la UI, (3) enviar un mensaje y esperar `wait_for_selector(".message.complete")`, (4) verificar el contenido final.

*(Esta sección no tiene Técnicas avanzadas — el módulo se centra en E2E y no tiene implementaciones adicionales del manual.)*

**Errores comunes:**
- ❌ Asumir que si la API funciona, la UI también → SSE tiene comportamientos específicos de la capa de presentación ✅ Siempre testear la UI con Playwright
- ❌ Tests sin `wait_for_selector` → race condition entre el streaming y la verificación ✅ Esperar explícitamente a que el mensaje esté completo
- ❌ No testear reconexión tras desconexión → el cliente SSE puede no recuperarse automáticamente ✅ Incluir test de reconexión
- ❌ Tests E2E en CI sin servidor levantado → el test pasa localmente pero falla en CI ✅ Usar fixture de pytest que levanta el servidor antes del test

**En producción:**
```bash
# Arrancar servidor mock
uvicorn modules.11-playwright-streaming.src.mock_chat_server:app --port 8765 &

# Ejecutar tests E2E
pytest modules/11-playwright-streaming/tests/ -m "not slow" -q
```
Referencia cruzada: para observabilidad del pipeline de streaming → módulo 12.

**Caso real:** Plataforma de generación de contenido para medios con editor IA. Los tests de API pasaban correctamente, pero el 4% de los usuarios reportaban que el texto se "cortaba" a mitad de frase. Los tests Playwright con interceptación SSE revelaron que el cliente no manejaba correctamente chunks que llegaban partidos en mitad de un carácter Unicode multibyte. El bug no era detectable sin un test E2E con navegador real.

**Ejercicios:**
- 🟢 Añade un test que verifique que si el servidor devuelve un error HTTP 500, la UI muestra un mensaje de error — no una pantalla en blanco.
- 🟡 Implementa un test que simule una desconexión SSE a mitad del streaming y verifica que el cliente intenta reconectar y el mensaje queda marcado como incompleto.
- 🔴 Añade tests de regresión visual con `page.screenshot()`: captura el estado de la UI antes del primer token, durante el streaming y después del mensaje completo. Verifica que los tres estados tienen el markup correcto.

- [ ] **Step 2: Verificar 8 secciones y sidebar**

- [ ] **Step 3: Commit**
```bash
git add site/modulos/11-playwright-streaming.md
git commit -m "docs: rewrite module 11 with 8-section template"
```

---

## Task 12: Módulo 12 — observability

**Files:**
- Modify: `site/modulos/12-observability.md`

- [ ] **Step 1: Reescribir**

**El problema:** Tu pipeline LLM tiene 3 segundos de latencia. ¿El problema está en el retriever, en el reranker o en la llamada al LLM? Sin trazas, la única forma de saberlo es añadir prints y volver a ejecutar. Con OpenTelemetry, cada etapa genera un span con su duración exacta. En producción, un pipeline sin observabilidad es una caja negra — solo sabes que algo falla, no dónde.

**Cómo funciona:**
- Span OTel: unidad de trazabilidad. Registra inicio, fin, duración y metadatos de una operación.
- `@trace`: decorador que envuelve una función y crea automáticamente un span con su nombre y duración.
- `Collector`: acumula los spans durante una ejecución y permite verificarlos en tests.
- Langfuse y Phoenix: plataformas de visualización de trazas para pipelines LLM. El lab genera trazas compatibles con ambas.

**Código paso a paso:** (1) Decorar funciones con `@trace`, (2) usar `get_collector()` como context manager, (3) verificar `span_count` y `total_latency`, (4) inspeccionar spans individuales por nombre.

**Técnicas avanzadas:** Presentar `TraceRecord` así: "Los 15 campos mandatorios de una traza son el mínimo para que el equipo de producción pueda diagnosticar incidencias sin pedir al desarrollador que reproduzca el problema." Mostrar `make_trace_record` y `validate_trace`.

**Errores comunes:**
- ❌ Spans sin correlación entre sí → no puedes reconstruir el pipeline completo ✅ Usar el mismo `trace_id` para todos los spans de una request
- ❌ Medir solo latencia total → no sabes qué etapa es el cuello de botella ✅ Un span por etapa: retrieval, reranking, generation
- ❌ Logs no estructurados (`print`) → no se pueden consultar en Langfuse ni Phoenix ✅ Usar structured logging con los 15 campos de `TraceRecord`
- ❌ No registrar tokens_in y tokens_out → no puedes calcular el coste por request ✅ Siempre registrar ambos contadores

**En producción:**
```
| Campo mandatorio  | Por qué importa                        |
|-------------------|---------------------------------------|
| trace_id          | Correlacionar spans de una request     |
| model_id          | Detectar regresiones por versión       |
| latency_ms        | SLA y alertas de rendimiento           |
| tokens_in/out     | Control de costes                      |
| error_type        | Clasificar incidencias                 |
```
Comando CI: `pytest modules/12-observability/tests/ -m "not slow" -q`
Referencia cruzada: para detectar degradación de latencia en el tiempo → módulo 13.

**Caso real:** Plataforma de sanidad con asistente de triaje. El equipo reportaba p95 de latencia de 4.2 segundos sin saber por qué. Tras instrumentar con `@trace` las tres etapas del pipeline, descubrieron que el reranker tardaba 2.8 segundos de media — el 67% de la latencia total. El retriever y el generador eran rápidos. La solución fue cachear los resultados del reranker para queries frecuentes, reduciendo el p95 a 1.6 segundos.

**Ejercicios:**
- 🟢 Añade un cuarto span al pipeline del lab (`@trace("postprocessing")`). Verifica que `collector.span_count` sube a 3 y que el nuevo span aparece en la lista.
- 🟡 Implementa un test que verifique que si una etapa tarda más de 2 segundos, el span correspondiente tiene `latency_ms > 2000`. Usa un mock que introduce un sleep controlado.
- 🔴 Genera 10 `TraceRecord` con `make_trace_record` simulando un pipeline real con varianza de latencia. Pásalos por `validate_trace` y construye un informe que muestre p50, p95 y p99 de latencia por etapa.

- [ ] **Step 2: Verificar 8 secciones y sidebar**

- [ ] **Step 3: Commit**
```bash
git add site/modulos/12-observability.md
git commit -m "docs: rewrite module 12 with 8-section template"
```

---

## Task 13: Módulo 13 — drift-monitoring

**Files:**
- Modify: `site/modulos/13-drift-monitoring.md`

- [ ] **Step 1: Reescribir**

**El problema:** El modelo no ha cambiado. Los prompts tampoco. Pero los usuarios se quejan de peor calidad. Esto es drift: la distribución de las queries de entrada ha cambiado y el modelo ya no responde igual de bien. PSI mide cuánto ha cambiado esa distribución. Sin monitorización de drift, una degradación silenciosa puede durar semanas antes de que lleguen suficientes quejas para detectarla.

**Cómo funciona:**
- PSI (Population Stability Index): compara la distribución de scores entre un período de referencia y el actual. Divide el rango de scores en bins y calcula la divergencia. PSI < 0.1: sin cambio. 0.1-0.2: cambio moderado. > 0.2: cambio significativo.
- `AlertHistory`: registra el resultado de cada evaluación. Calcula tendencias: `degrading` (≥2 de los últimos 3 dispararon alerta), `recovering` (primero disparó, los 2 últimos no), `stable` (exactamente 1 de los últimos 3).
- `evaluate_rules`: combina múltiples reglas (mean_drop + PSI) con lógica AND/OR.

**Código paso a paso:** (1) `compute_psi` sobre dos series de scores, (2) definir reglas con `mean_drop_alert` y `psi_alert`, (3) ejecutar `evaluate_rules`, (4) añadir resultados a `AlertHistory` y consultar `trend`.

**Técnicas avanzadas:** No hay contenido adicional del manual para este módulo — la implementación actual es completa. Esta sección puede omitirse o dedicarse a mostrar cómo combinar `AlertHistory` con Langfuse para visualización.

**Errores comunes:**
- ❌ PSI sin período de referencia establecido → cualquier comparación es arbitraria ✅ Definir explícitamente qué ventana temporal es el "baseline"
- ❌ Alertar en el primer PSI > 0.2 → puede ser un pico puntual ✅ Usar `AlertHistory` para confirmar tendencia antes de actuar
- ❌ Una sola regla de alerta → no distingue si el problema es la media o la distribución ✅ Combinar `mean_drop_alert` + `psi_alert`
- ❌ No actualizar el baseline periódicamente → el baseline queda obsoleto y los falsos positivos aumentan ✅ Rotar el baseline mensualmente o tras deployments

**En producción:**
```
| PSI       | Acción recomendada                      |
|-----------|----------------------------------------|
| < 0.10    | Ninguna — monitorización normal        |
| 0.10-0.20 | Investigar — posible cambio en inputs  |
| > 0.20    | Actuar — evaluar reentrenamiento       |
```
Comando CI (scheduled): `pytest modules/13-drift-monitoring/tests/ -m "not slow" -q`
Referencia cruzada: para instrumentar el pipeline que genera estos scores → módulo 12.

**Caso real:** Retailer con chatbot de recomendaciones de producto. En campaña de Navidad, las queries cambiaron drásticamente (más urgencia, menos comparativas). PSI subió a 0.31 en la primera semana de diciembre. `AlertHistory` marcó tendencia `degrading` tras 3 evaluaciones consecutivas. El equipo activó un modelo de respaldo entrenado con datos de campañas anteriores. Sin monitorización, habrían detectado el problema solo a través de quejas de usuarios.

**Ejercicios:**
- 🟢 Genera dos distribuciones de scores muy similares (ruido ±0.05) y calcula PSI. ¿Qué valor obtienes? Genera ahora una con shift de 0.15 — ¿el PSI supera 0.2?
- 🟡 Implementa una secuencia de 6 evaluaciones donde las primeras 3 disparan alerta y las últimas 3 no. Verifica que `AlertHistory.trend` es `recovering`.
- 🔴 Diseña un sistema de monitorización completo: 30 días de datos simulados con degradación progresiva. Usa `evaluate_rules` y `AlertHistory` para detectar el punto exacto en que el sistema debería haber alertado.

- [ ] **Step 2: Verificar 8 secciones y sidebar**

- [ ] **Step 3: Commit**
```bash
git add site/modulos/13-drift-monitoring.md
git commit -m "docs: rewrite module 13 with 8-section template"
```

---

## Task 14: Módulo 14 — embedding-eval

**Files:**
- Modify: `site/modulos/14-embedding-eval.md`

- [ ] **Step 1: Reescribir**

**El problema:** Tu sistema de búsqueda semántica funcionaba bien. Ahora los candidatos relevantes aparecen en posición 8 o 9 en lugar de en el top-3. El modelo de embeddings no ha cambiado. ¿Qué pasó? Los datos del corpus han cambiado — el centroide semántico se ha desplazado. Sin detección de drift semántico, este tipo de degradación es invisible hasta que los usuarios se quejan.

**Cómo funciona:**
- Similitud coseno: distancia angular entre dos vectores de embedding. 1.0 = idénticos, 0.0 = ortogonales.
- `MockEmbeddingModel`: genera embeddings deterministas con hashlib. Sin llamadas a OpenAI — todos los tests son reproducibles.
- `EmbeddingRegressionChecker`: compara si el candidato se aleja semánticamente del baseline más del threshold permitido.
- `compute_centroid_shift`: calcula la distancia coseno entre el centroide del corpus de referencia y el corpus actual. Mide drift a nivel de corpus completo, no de query individual.
- NDCG@k, MRR@k, MAP@k: métricas de ranking que miden si los documentos relevantes aparecen en las posiciones más altas.

**Código paso a paso:** (1) Crear `MockEmbeddingModel` y `SemanticSimilarityMetric`, (2) medir similitud entre expected y actual, (3) usar `compute_centroid_shift` con dos corpus, (4) configurar `semantic_drift_alert`.

**Técnicas avanzadas:** Presentar `RetrievalMetrics` así: "La similitud coseno mide si dos respuestas son parecidas. NDCG, MRR y MAP miden si los documentos relevantes aparecen donde el usuario los espera — en las posiciones más altas del ranking."

**Errores comunes:**
- ❌ Similitud coseno sin threshold calibrado → no sabes qué score indica "suficientemente similar" ✅ Calibrar el threshold con pares de respuestas humanas etiquetadas
- ❌ Evaluar solo pares individuales → no detecta drift del corpus completo ✅ Usar `compute_centroid_shift` periódicamente
- ❌ NDCG@k sin definir k → k depende de cuántos resultados muestra la UI ✅ Usar el mismo k que muestra la interfaz (típicamente 3, 5 o 10)
- ❌ Asumir que embeddings de OpenAI son deterministas → los modelos de embedding también pueden cambiar ✅ Usar `MockEmbeddingModel` en tests, embeddings reales en evaluación periódica

**En producción:**
```
| Métrica           | Umbral recomendado |
|-------------------|--------------------|
| similitud coseno  | ≥ 0.70             |
| centroid_shift    | < 0.10             |
| NDCG@5            | ≥ 0.75             |
| MRR@5             | ≥ 0.70             |
```
Comando CI: `pytest modules/14-embedding-eval/tests/ -m "not slow" -q`
Referencia cruzada: para monitorizar drift semántico en el tiempo → módulo 13.

**Caso real:** Plataforma de empleo con búsqueda semántica de candidatos. Tras incorporar nuevas ofertas de trabajo de un sector emergente (IA generativa), el centroide del corpus de candidatos se desplazó 0.18 puntos. NDCG@5 bajó de 0.81 a 0.64 — los reclutadores tardaban el doble en encontrar candidatos relevantes. El equipo detectó el shift con `compute_centroid_shift` antes de que llegaran quejas y reindexó el corpus con el nuevo vocabulario del sector.

**Ejercicios:**
- 🟢 Mide la similitud coseno entre "El envío tarda 3 días" y "Los pedidos se entregan en 72 horas". ¿El resultado supera 0.7? ¿Qué indica sobre la calidad del embedding mock?
- 🟡 Genera dos corpus de 10 documentos cada uno con un shift semántico claro (uno sobre e-commerce, otro sobre sanidad). Verifica que `compute_centroid_shift` detecta la diferencia y supera el threshold de 0.1.
- 🔴 Implementa una evaluación de retrieval completa con `evaluate_retrieval`: 5 queries, sus documentos relevantes y los rankings devueltos por tu sistema. Calcula NDCG@3, MRR@3 y MAP@3. ¿Cuál es el indicador más sensible en tu dataset?

- [ ] **Step 2: Verificar 8 secciones y sidebar**

- [ ] **Step 3: Commit**
```bash
git add site/modulos/14-embedding-eval.md
git commit -m "docs: rewrite module 14 with 8-section template"
```

---

## Task 15: Ampliar glosario

**Files:**
- Modify: `site/guia/conceptos.md`

- [ ] **Step 1: Añadir los nuevos términos al glosario**

Añadir las siguientes secciones y términos al final de `site/guia/conceptos.md`:

**Sección: Evaluación estadística**
- `Cohen kappa (κ)` — Medida de acuerdo entre dos anotadores que corrige el acuerdo por azar. κ < 0.41: pobre. 0.41-0.60: moderado. 0.61-0.80: sustancial. > 0.80: casi perfecto. (Landis & Koch, 1977)
- `Bootstrap IC95` — Intervalo de confianza al 95% calculado remuestreando los datos N veces. Más robusto que el z-test cuando la distribución no es normal o la muestra es pequeña.
- `Kruskal-Wallis` — Test no paramétrico para detectar si las distribuciones de K grupos independientes difieren. Se usa en el lab para detectar sesgo demográfico.

**Sección: Seguridad y guardrails**
- `False refusal rate` — Fracción de queries legítimas que el modelo rechaza incorrectamente. Un guardrail que bloquea demasiado tiene false_refusal_rate alta.
- `Canary token` — Valor único inyectado en el system prompt para detectar si el modelo lo filtra en las respuestas.
- `Excessive agency` — Riesgo OWASP LLM donde el agente tiene más permisos de los necesarios y puede ejecutar acciones destructivas sin autorización.

**Sección: Evaluación de retrieval**
- `NDCG@k` (Normalized Discounted Cumulative Gain) — Mide si los documentos relevantes aparecen en las primeras k posiciones. Penaliza más los errores en la posición 1 que en la posición k.
- `MRR@k` (Mean Reciprocal Rank) — Posición media del primer documento relevante en los k resultados. 1.0 = siempre primero.
- `MAP@k` (Mean Average Precision) — Precision promedio calculada en cada posición donde aparece un documento relevante. Considera todos los documentos relevantes, no solo el primero.

**Sección: Trazabilidad**
- `IAA` (Inter-Annotator Agreement) — Medida del grado en que diferentes anotadores asignan las mismas etiquetas. Se cuantifica con Cohen kappa u otras métricas según el tipo de anotación.
- `Centroid shift` — (ya existe en el glosario — no duplicar)
- `Trajectory evaluation` — Evaluación de la secuencia de acciones de un agente, no solo del resultado final. Verifica que el agente llegó al resultado correcto por el camino correcto.

- [ ] **Step 2: Verificar que no hay duplicados con las definiciones existentes**

- [ ] **Step 3: Commit**
```bash
git add site/guia/conceptos.md
git commit -m "docs: expand glossary with new terms from module rewrites"
```

---

## Self-Review

**Spec coverage:**
- ✓ 14 módulos reescritos con plantilla de 8 secciones
- ✓ Integración natural del contenido del manual (sin encabezado que delata el origen)
- ✓ Caso real de producción en cada módulo (sectores distintos)
- ✓ 3 ejercicios graduados por módulo (🟢/🟡/🔴)
- ✓ Glosario ampliado con nuevos términos
- ✓ Módulo 11 sin sección "Técnicas avanzadas" (documentado en el plan)

**Placeholder scan:** Sin TBDs ni referencias a "similar al task anterior". Cada task tiene el contenido completo.

**Type consistency:** Los nombres de clases y métodos son consistentes con los que aparecen en el código fuente (`src/`) verificado durante el brainstorming.
