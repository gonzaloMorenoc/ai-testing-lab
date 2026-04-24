# Diseño: Implementación de los 12 módulos restantes

**Fecha:** 2026-04-24
**Autor:** Gonzalo Moreno
**Estado:** aprobado

---

## Contexto

El repo `ai-testing-lab` tiene 13 módulos didácticos de testing de LLMs y chatbots. El módulo 01 (`primer-eval`) está implementado y funcional. Los módulos 02-13 tienen estructura y README pero sin código.

**Objetivo:** implementar los 12 módulos restantes con calidad de portfolio público.

---

## Decisiones clave

| Decisión | Elección | Motivo |
|----------|----------|--------|
| Objetivo del repo | Portfolio + visibilidad pública | Sin gestión activa de comunidad |
| Infraestructura requerida | Ninguna por defecto | `uv sync + pytest` sin Docker ni Ollama |
| Peso de cada módulo | Medio | 2-3 archivos src, 8-12 tests, solución de ejercicio |
| Orden de implementación | Eje evaluación → seguridad → infraestructura | El eje de evaluación es la base conceptual |
| Estrategia de paralelismo | Batches paralelos por eje temático | 3-4x más rápido que secuencial |

---

## Contrato de módulo

Todos los módulos cumplen estas garantías sin excepción:

### Estructura fija

```
modules/NN-nombre/
├── conftest.py                    # sys.path + fixtures del módulo
├── src/
│   ├── __init__.py
│   ├── [componente_1].py          # máx. 150 líneas
│   └── [componente_2].py          # máx. 150 líneas
└── tests/
    ├── __init__.py
    ├── conftest.py                 # fixtures de tests
    └── test_[nombre].py           # 8-12 tests
```

### Garantías de ejecución

- `pytest modules/NN/tests/ -m "not slow" --record-mode=none` → pasa **sin API key, sin Docker, sin Ollama**
- `pytest modules/NN/tests/ -m slow` → pasa con `GROQ_API_KEY` o se salta automáticamente con `pytest.skip`
- Cada módulo es **completamente independiente**: no importa nada de otros módulos

### Distribución de tests (8-12 por módulo)

| Tipo | Cantidad | Marca |
|------|----------|-------|
| Happy path | 3-4 | *(ninguna)* |
| Casos negativos | 2-3 | *(ninguna)* |
| Edge cases | 1-2 | *(ninguna)* |
| Con LLM real | 1 | `@pytest.mark.slow` |

### Ejercicios

- El enunciado ya está en el README de cada módulo (creado en Fase 1)
- La solución se añade en `exercises/solutions/NN-[nombre]-solution.py`

---

## Batch 1 — Eje de evaluación (módulos 02-06)

El módulo 02 actúa como plantilla del batch.

### Módulo 02 — ragas-basics *(plantilla)*

**Qué enseña:** Las 4 métricas RAGAS más usadas en pipelines RAG.

| Archivo | Responsabilidad |
|---------|----------------|
| `src/rag_pipeline.py` | RAG mínimo con knowledge base in-memory (dict), sin ChromaDB |
| `src/ragas_evaluator.py` | Wrapper simplificado de RAGAS que expone faithfulness, answer_relevancy, context_precision, context_recall |

**Tests:**
1. Faithfulness alta cuando respuesta está fundamentada en contexto
2. Faithfulness baja cuando respuesta contiene alucinación
3. Answer relevancy alta para pregunta pertinente
4. Answer relevancy baja para respuesta fuera de tema
5. Context precision con chunks todos relevantes
6. Context precision con chunks mezclados (relevantes + ruido)
7. Dataset con múltiples casos evaluados en batch
8. Score por debajo del umbral lanza `AssertionError` con mensaje claro
9. `@pytest.mark.slow` — métricas reales con Groq

---

### Módulo 03 — llm-as-judge

**Qué enseña:** Cómo construir un juez LLM desde cero: G-Eval y DAG Metric.

| Archivo | Responsabilidad |
|---------|----------------|
| `src/geval_judge.py` | G-Eval con criterios en lenguaje natural; versión mock determinista + versión real con LLM |
| `src/dag_metric.py` | Árbol de decisión acíclico que evalúa outputs con reglas booleanas sin LLM |

**Tests:**
1. G-Eval mock con rúbrica de relevancia devuelve score en [0,1]
2. G-Eval mock con rúbrica de toxicidad detecta texto tóxico
3. DAG con regla "contiene palabra clave" evalúa correctamente
4. DAG con regla compuesta (AND/OR) evalúa correctamente
5. Position bias demostrado: mismo contenido en orden A/B produce scores distintos
6. Verbosity bias demostrado: respuesta larga puntúa más que corta con mismo contenido
7. G-Eval real requiere LLM (se salta sin `GROQ_API_KEY`)
8. `@pytest.mark.slow` — G-Eval real con Groq

---

### Módulo 04 — multi-turn

**Qué enseña:** Testing de conversaciones con múltiples turnos y retención de contexto.

| Archivo | Responsabilidad |
|---------|----------------|
| `src/conversation.py` | Historial de conversación como lista de mensajes; método `add_turn()`, `to_deepeval_format()` |
| `src/multi_turn_rag.py` | RAG que recibe historial y genera respuesta coherente con contexto acumulado |

**Tests:**
1. Información del turno 1 está disponible en el turno 3
2. Contradicción entre turno 2 y turno 4 detectada
3. Conversación de 5 turnos sin pérdida de coherencia
4. `ConversationalTestCase` de DeepEval construido desde historial
5. `KnowledgeRetentionMetric` mock detecta pérdida de información
6. `ConversationCompletenessMetric` mock detecta conversación incompleta
7. Reset de conversación limpia el historial
8. `@pytest.mark.slow` — evaluación real con Groq

---

### Módulo 05 — prompt-regression

**Qué enseña:** Regression testing de prompts con Promptfoo y detección de degradaciones.

| Archivo | Responsabilidad |
|---------|----------------|
| `src/prompt_registry.py` | Registro de prompts versionados (v1, v2) como diccionario con metadata |
| `src/regression_checker.py` | Compara scores de dos versiones y reporta regresiones (caída > umbral configurable) |
| `promptfooconfig.yaml` | Config Promptfoo real: 2 prompts × 1 modelo (Groq llama3) |

**Tests:**
1. Versión nueva mejora score → sin regresión
2. Versión nueva baja score > 10% → regresión detectada
3. Empate dentro del margen de tolerancia → sin regresión
4. Registry devuelve prompt correcto por versión y nombre
5. `promptfooconfig.yaml` es YAML válido y tiene estructura correcta
6. Reporte de regresión incluye delta y porcentaje de cambio
7. Múltiples métricas: pasa en relevancia, falla en fidelidad
8. `@pytest.mark.slow` — Promptfoo eval real con Groq

---

### Módulo 06 — hallucination-lab

**Qué enseña:** Detección de alucinaciones con claim extraction y groundedness check.

| Archivo | Responsabilidad |
|---------|----------------|
| `src/claim_extractor.py` | Extrae claims de una respuesta (split por frases + filtro de longitud mínima) |
| `src/groundedness_checker.py` | Verifica cada claim contra el contexto recuperado (overlap de tokens + umbral) |

**Tests:**
1. Respuesta completamente fiel al contexto → groundedness alta
2. Respuesta con un claim inventado → groundedness media detectada
3. Respuesta totalmente alucinada → groundedness baja
4. Sin contexto de recuperación → score 0.0
5. Claim extractor produce lista no vacía para respuesta normal
6. Claim extractor produce lista vacía para respuesta de una palabra
7. Umbral configurable: 0.6 pasa donde 0.8 falla
8. `HallucinationMetric` de DeepEval con mock
9. `@pytest.mark.slow` — métricas reales con Groq

---

## Batch 2 — Eje de seguridad (módulos 07-09)

El módulo 07 actúa como plantilla del batch. El patrón central es: **`model_fn` callable + scanner**.

```python
# Interfaz común de todos los módulos de seguridad
def model_fn(prompt: str) -> str:
    """El sistema bajo prueba. Puede ser mock o LLM real."""
    ...
```

### Módulo 07 — redteam-garak *(plantilla)*

**Qué enseña:** Red teaming sistemático con colección de prompts de ataque.

| Archivo | Responsabilidad |
|---------|----------------|
| `src/attack_prompts.py` | 15 prompts de ataque reales categorizados: DAN, encoding (base64/leetspeak), roleplay, crescendo, indirect injection |
| `src/vulnerability_scanner.py` | Ejecuta prompts contra `model_fn`, detecta si el modelo "cede" (heurístico: ausencia de rechazo), produce reporte con hit rate |

**Tests:**
1. Modelo seguro (mock que siempre rechaza) → hit rate = 0%
2. Modelo vulnerable (mock que siempre cumple) → hit rate = 100%
3. DAN prompt detectado como ataque ejecutado
4. Encoding attack (base64) detectado
5. Roleplay jailbreak detectado
6. Reporte incluye categoría, prompt, respuesta y veredicto
7. Hit rate por categoría calculado correctamente
8. `@pytest.mark.slow` — scan real contra Groq

---

### Módulo 08 — redteam-deepteam

**Qué enseña:** OWASP Top 10 LLM 2025 automatizado con DeepTeam.

| Archivo | Responsabilidad |
|---------|----------------|
| `src/owasp_scenarios.py` | 10 dataclasses con escenarios del OWASP Top 10 LLM 2025: descripción, prompt de ataque, criterio de éxito |
| `src/deepteam_runner.py` | Ejecuta escenarios contra `model_fn` y produce reporte JSON con veredicto por vulnerabilidad |

**Tests:**
1. LLM01 (Prompt Injection directa) detectado en modelo vulnerable
2. LLM02 (Sensitive Info Disclosure) detectado cuando modelo revela system prompt
3. LLM06 (Excessive Agency) detectado cuando modelo ejecuta acción no autorizada
4. LLM09 (Misinformation/Hallucination) detectado con claim checker
5. Modelo con guardrails pasa todos los escenarios
6. Reporte JSON tiene estructura correcta (schema validado con Pydantic)
7. Escenarios son independientes: fallo en uno no interrumpe los demás
8. `@pytest.mark.slow` — scan real con Groq

---

### Módulo 09 — guardrails

**Qué enseña:** Validación de inputs y outputs con Guardrails AI y NeMo Guardrails.

| Archivo | Responsabilidad |
|---------|----------------|
| `src/input_validator.py` | Valida inputs: PII detection (regex: email, teléfono, SSN), toxicity check (lista de términos), longitud máxima |
| `src/output_validator.py` | Valida outputs: no contiene system prompt leakeado, no contiene PII de la KB, estructura JSON cuando se espera |

**Tests:**
1. Email en input → bloqueado con razón clara
2. Teléfono en input → bloqueado
3. Input limpio → pasa validación
4. Output con system prompt → rechazado
5. Output con PII → rechazado
6. Output JSON válido → aceptado
7. Output JSON inválido → rechazado con detalle del error
8. Pipeline completo: input con PII → bloqueado antes de llegar al LLM
9. `@pytest.mark.slow` — Guardrails AI real con Groq

---

## Batch 3 — Eje de infraestructura (módulos 10-13)

El módulo 10 actúa como plantilla del batch.

### Módulo 10 — agent-testing *(plantilla)*

**Qué enseña:** Evaluación de agentes: tool selection, argumentos y trayectorias.

| Archivo | Responsabilidad |
|---------|----------------|
| `src/simple_agent.py` | Agente mínimo con 3 tools: `search(query)`, `calculate(expr)`, `format_response(data)`. El agente decide qué tool usar dado un input (lógica determinista basada en keywords) |
| `src/trajectory_evaluator.py` | Evalúa si la secuencia de tool calls coincide con la trayectoria esperada (exact match + partial credit) |

**Tests:**
1. Query de búsqueda → tool `search` elegida
2. Query matemática → tool `calculate` elegida
3. Tool incorrecta → `ToolCallAccuracy` = 0
4. Argumento incorrecto en tool correcta → penalización parcial
5. Trayectoria de 3 steps completa y correcta → score 1.0
6. Trayectoria con step extra → penalización
7. Trayectoria con step faltante → penalización
8. `AgentGoalAccuracy` mock: tarea completada vs. no completada
9. `@pytest.mark.slow` — agente real con Groq tool calling

---

### Módulo 11 — playwright-streaming

**Qué enseña:** Testing E2E de UIs de chatbot con streaming SSE.

| Archivo | Responsabilidad |
|---------|----------------|
| `src/mock_chat_server.py` | Servidor FastAPI con endpoint `/chat` que hace streaming SSE token a token (50ms delay entre tokens). Se levanta como fixture de pytest con `uvicorn` en thread separado en puerto aleatorio |

**Tests (con Playwright):**
1. Input enviado → respuesta aparece en DOM
2. Streaming: el texto aparece incrementalmente (verificado con polling)
3. Respuesta completa antes del assert final (esperado con `data-complete="true"`)
4. Assertion regex sobre texto no determinista
5. Input vacío → mensaje de error en UI
6. Screenshot del estado final guardado como artefacto
7. Iframe embebido: chatbot dentro de iframe funciona igual
8. `@pytest.mark.slow` — test real contra demo `streamlit-chat` de Docker

---

### Módulo 12 — observability

**Qué enseña:** Instrumentación OTel y tracing de pipelines LLM sin vendor lock-in.

| Archivo | Responsabilidad |
|---------|----------------|
| `src/tracer.py` | Decorador `@trace(name, attributes)` que captura input, output, latencia y errores como OTel spans |
| `src/mock_collector.py` | Colector OTel in-memory para tests: recibe spans sin necesitar Langfuse/Phoenix real. Expone `get_spans()` para assertions |

**Tests:**
1. Función decorada con `@trace` genera un span en el colector
2. Span contiene atributos: `input`, `output`, `duration_ms`
3. Excepción en función trazada → span con `status=ERROR`
4. Spans anidados (función A llama función B, ambas trazadas) → relación padre-hijo correcta
5. Colector acumula spans de múltiples llamadas
6. `get_spans()` filtra por nombre de span
7. Exportación a dict para assert de estructura
8. `@pytest.mark.slow` — exportación real a Langfuse local

---

### Módulo 13 — drift-monitoring

**Qué enseña:** Detección de drift semántico en producción con alertas configurables.

| Archivo | Responsabilidad |
|---------|----------------|
| `src/drift_detector.py` | Calcula PSI (Population Stability Index) entre distribución de referencia y distribución actual de scores. Implementado con numpy puro |
| `src/alert_rules.py` | Reglas configurables: alerta si PSI > umbral, alerta si media cae > X%, alerta si p95 supera límite |

**Tests:**
1. Distribuciones idénticas → PSI ≈ 0 → sin drift
2. Distribución muy distinta → PSI > 0.2 → drift detectado
3. Media cae 20% → alerta disparada
4. Media cae 5% → sin alerta (dentro del margen)
5. P95 supera límite → alerta disparada
6. Múltiples reglas: todas pasan → sin alerta
7. Múltiples reglas: una falla → alerta con detalle de qué regla
8. Reporte incluye timestamp, métrica evaluada y valores observados
9. `@pytest.mark.slow` — drift real sobre scores de Langfuse exportados

---

## Resumen

| Batch | Módulos | Tests nuevos | Archivos src nuevos | Plantilla |
|-------|---------|-------------|--------------------|---------:|
| 1 — Evaluación | 02, 03, 04, 05, 06 | ~43 | 11 | 02-ragas-basics |
| 2 — Seguridad | 07, 08, 09 | ~25 | 6 | 07-redteam-garak |
| 3 — Infraestructura | 10, 11, 12, 13 | ~33 | 8 | 10-agent-testing |
| **Total** | **12** | **~110** | **25** | |

Más 12 soluciones de ejercicios en `exercises/solutions/`.

---

## Lo que NO está en el scope

- Implementar los demos de Docker (`simple-rag`, `streamlit-chat`, `rasa-intent-bot`, `vulnerable-bot`)
- Implementar golden datasets reales en `goldens/`
- Configurar GitHub Pages
- Añadir cassettes VCR pregrabados con llamadas reales a Groq (los tests slow hacen llamadas en vivo o se saltan)
