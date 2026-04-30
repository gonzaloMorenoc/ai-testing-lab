# Spec: Mejora de contenido del lab — Plantilla de 8 secciones

**Fecha:** 2026-04-30
**Estado:** Aprobado

---

## Problema

Las páginas de módulo actuales son insuficientes para un QA senior o ingeniero de ML/NLP. Presentan un snippet de código y una frase de "por qué importa", sin explicar el mecanismo, sin contexto de uso real, y con secciones "Nuevas implementaciones (Manual QA AI v12)" que parecen volcados de código sin contexto. El proyecto no cumple su objetivo de ser un referente didáctico de calidad.

## Objetivo

Reescribir las 14 páginas de módulo del site VitePress (`site/modulos/NN-nombre.md`) aplicando una plantilla uniforme de 8 secciones que:

- Sea general y abstracta en las 6 primeras secciones (aprende el concepto, aplícalo a tu dominio)
- Incluya un caso real de producción en la sección 7 (contexto concreto con dominio específico)
- Termine con ejercicios prácticos graduados en la sección 8
- Integre de forma natural el contenido del manual QA AI v12 donde aporte valor, sin encabezados que delaten el origen

## Audiencia objetivo

**Principal:** QA senior con experiencia en automatización (pytest, Selenium, Playwright, API testing) que está incorporando testing de LLMs a su flujo de trabajo. Conoce pytest a fondo, pero no conoce RAGAS, DeepEval ni G-Eval.

**Secundaria:** Ingeniero/a de ML o NLP que conoce los conceptos (faithfulness, embeddings, drift) pero quiere aprender a testearlos de forma sistemática en CI.

El contenido debe ser accesible para el perfil principal sin aburrir al secundario.

---

## Plantilla de 8 secciones

### 1. El problema (~100-150 palabras, sin código)

Describe el riesgo genérico que este módulo resuelve. Escrito en segunda persona ("cambias el prompt y..."). Sin mencionar sectores ni empresas — eso va en la sección 7. El objetivo es que cualquier lector, independientemente de su dominio, sienta que este problema le afecta.

### 2. Cómo funciona (~150-200 palabras + diagrama ASCII si aplica)

Explica el mecanismo interno antes de mostrar código. El QA senior entiende POR QUÉ el número sale así, no solo cómo llamar a la función. Incluye diagramas ASCII de flujo cuando el pipeline tiene más de 2 etapas.

### 3. Código paso a paso (3-4 fragmentos progresivos)

No un bloque monolítico. Se construye en pasos: primero la estructura básica, luego se añade complejidad. Entre fragmentos hay 1-2 frases de contexto. Los comentarios en el código explican el WHY, no el WHAT.

### 4. Técnicas avanzadas (solo si aporta valor real)

Integra el contenido del manual QA AI v12 de forma natural. Aparece precedido de 2-3 frases que explican cuándo y por qué necesitas ir más allá del código básico. Sin referencia al manual, sin numeración de capítulos. Se omite en módulos donde no hay contenido adicional relevante (ej: módulo 11).

### 5. Errores comunes (3-5 items)

Los anti-patterns más frecuentes que un QA senior cometería con esta técnica. Formato:

```
❌ Lo que parece correcto pero no lo es — consecuencia concreta
✅ La forma correcta — por qué funciona mejor
```

### 6. En producción (~150 palabras + tabla de thresholds si aplica)

Cómo integrar esta técnica en un pipeline real:
- Thresholds recomendados por entorno (PR / Staging / Canary / Producción)
- Comando pytest para CI
- Qué monitorizar en producción
- Referencias cruzadas a módulos relacionados (ej: "para monitorizar este score en producción → módulo 13")

### 7. Caso real en producción (~200 palabras, narrativo)

Un escenario específico con empresa ficticia pero verosímil. Estructura:
- Contexto: empresa, producto, escala
- Problema: qué falló o qué riesgo detectaron
- Solución: cómo aplicaron la técnica de este módulo
- Resultado: qué detectaron o evitaron

Cada módulo usa un sector diferente para que el conjunto del lab cubra distintos dominios.

### 8. Ejercicios (3 retos)

- 🟢 **Básico** — autocontenido, modifica un parámetro y observa el efecto. Resolvible en 5-10 minutos.
- 🟡 **Intermedio** — requiere escribir código nuevo dentro del módulo. Resolvible en 20-30 minutos.
- 🔴 **Avanzado** — integra este módulo con otro del lab o simula un escenario de producción complejo. Resolvible en 45-60 minutos.

---

## Plan módulo por módulo

| Módulo | Caso real (sector) | Técnicas avanzadas integradas | Errores comunes principales |
|--------|-------------------|------------------------------|----------------------------|
| **01** primer-eval | Fintech: chatbot de soporte detecta bajada de relevancy tras cambio de prompt | `QAGateChecker` (3 niveles de riesgo) + `EvalDesignChecker` (AP-01 a AP-10) | Threshold arbitrario / solo happy path / mismo LLM como juez |
| **02** ragas-basics | Legal: asistente de contratos con retriever que devuelve chunks irrelevantes | Clusters de sinónimos de dominio jurídico | Confundir context precision con recall / evaluar solo el generador |
| **03** llm-as-judge | RRHH: comparación A/B de modelos para cribar CVs — position bias invalida resultados | `JudgeBias` (5 sesgos) + Cohen kappa (IAA) | Juez no calibrado / verbosity bias / sin acuerdo inter-anotador |
| **04** multi-turn | E-commerce: chatbot que olvida la dirección de envío tras 4 turnos | `MultiTurnEvaluator` (7 métricas deterministas) | Ventana de contexto no testeada / no verificar coreferencialidad |
| **05** prompt-regression | SaaS B2B: equipo de producto cambia el prompt cada sprint sin saber si mejora | `VarianceEvaluator` (bootstrap IC95) + `CIGatePipeline` (4 etapas) | Diferencia sin test estadístico / muestra < 30 casos |
| **06** hallucination-lab | Salud: chatbot de síntomas contradice el contexto médico con negaciones | `HallucinationClassifier` (taxonomía 2 niveles Ji et al. 2023) | Faithfulness no detecta negaciones / no distinguir intrínseco vs extrínseco |
| **07** redteam-garak | Seguros: auditoría de seguridad antes del despliegue del modelo | `RobustnessSuite` (7 perturbaciones) | Solo testear DAN / ignorar many-shot e indirect injection |
| **08** redteam-deepteam | EdTech: agente con acceso a APIs externas expuesto a usuarios finales | `SafetySuite` (refusal rate + false refusal + bias demográfico) | No balancear refusal con false refusal / ignorar riesgos de agencia |
| **09** guardrails | RRHH: chatbot que filtra datos de candidatos con PII en respuestas | `PIICanary` (canary tokens + 6 patrones regex ES+EN) | Validar solo el input / no testear fugas del system prompt |
| **10** agent-testing | Logística: agente de planificación de rutas que llama herramientas incorrectas | `AgentPolicy` (allowed tools + sandbox + human approval) | No verificar trayectoria / `eval()` inseguro / sin límite de iteraciones |
| **11** playwright-streaming | Media: interfaz de generación de contenido con streaming que corrompe tokens | — (no hay técnicas avanzadas adicionales) | No testear SSE / asumir que si la API funciona la UI también |
| **12** observability | Sanidad: plataforma que no sabe qué etapa del pipeline añade latencia | `TraceRecord` (15 campos mandatorios) | Spans sin correlación / no medir por etapa / logs no estructurados |
| **13** drift-monitoring | Retail: calidad del chatbot de recomendaciones cae en campaña de Navidad | AlertHistory + reglas PSI compuestas | PSI sin periodo de referencia claro / alertas sin tendencias históricas |
| **14** embedding-eval | Empleo: candidatos relevantes dejan de aparecer en búsqueda semántica | `RetrievalMetrics` (NDCG@k, MRR@k, MAP@k) | Similitud coseno sin threshold calibrado / drift de corpus no detectado |

---

## Cambios adicionales

**`site/guia/conceptos.md`** — Ampliar el glosario con los nuevos términos introducidos en la reescritura: `IAA`, `Cohen kappa`, `bootstrap IC95`, `false refusal rate`, `centroid shift`, `NDCG@k`, `canary token`, `trajectory evaluation`.

**Encabezados eliminados** — Se elimina el encabezado "Nuevas implementaciones (Manual QA AI v12)" de los 10 módulos donde aparece. El contenido se integra en la sección 4 o se elimina si no aporta valor en el nuevo contexto.

---

## Criterios de éxito

- Las 14 páginas siguen la plantilla de 8 secciones sin excepciones
- No aparece ninguna referencia al "Manual QA AI v12" en el site
- Cada módulo tiene un caso real de dominio diferente
- Cada módulo tiene exactamente 3 ejercicios graduados (🟢 / 🟡 / 🔴)
- El glosario cubre todos los términos técnicos usados en el site
- Un QA senior sin experiencia en LLMs puede completar el módulo 01 y entender qué hace y por qué

---

## Fuera de alcance

- Cambios en el código Python de los módulos (`src/`, `tests/`)
- Nuevos módulos (15 en adelante)
- Cambios en el diseño visual o la estructura de navegación del site
- Traducciones
