# Auditoría del repositorio `ai-testing-lab` contra el Manual QA AI v13

**Fecha:** 2026-05-12
**Manual auditado:** `docs/Manual_QA_AI_Definitivo_v13.pdf` (114 pp, 33 capítulos + 4 apéndices, v13.6 según portada)
**Repo auditado:** `gonzaloMorenoc/ai-testing-lab` · rama `main` · 14 módulos

---

## TL;DR

| Indicador | Valor |
|---|---|
| Cobertura técnica del manual | **~72 %** (24 de 33 capítulos cubiertos por código; 6 gaps importantes) |
| Tests reales en el repo | **402** (el README y el site siguen anunciando 382 — desincronía de marketing) |
| Módulos completos y alineados | 11 de 14 |
| Páginas del site VitePress vs capítulos del manual | 7 guías + 14 módulos = **21 páginas**; el manual tiene 33 capítulos → ~64 % |
| Golden datasets por debajo del mínimo del manual (§9.2: ≥100) | **14 de 14** (rango actual: 8–15 entradas) |
| Gaps críticos no implementados | 6 (Cost-aware QA, Retrieval avanzado, HITL, Robustness dedicado, Cap. 26 antipatrones operativos, Apéndice D caso e2e) |

**Veredicto:** el repo está en muy buen estado técnico, pero el manual v13 ha crecido por encima de él. Hay seis huecos accionables que, si se cierran, llevarían la cobertura del manual del 72 % al 95 %+.

---

## 1. Mapa de cobertura capítulo a capítulo

Leyenda: ✅ cubierto · 🟡 parcial · ❌ falta · 📘 conceptual (debería estar en `site/guia/`)

| Cap. | Título manual v13 | Módulo/página del repo | Estado |
|---:|---|---|:--:|
| 01 | Introducción a la IA generativa | `site/guia/index.md` | 🟡 sin paradigmas, sin tabla 1.5 ISTQB |
| 02 | Fundamentos técnicos LLMs | — | 📘 falta página propia |
| 03 | Riesgos, calidad y marco normativo | — | ❌ EU AI Act / ISO 25010 sin reflejar |
| 04 | Por qué QA AI no es QA tradicional | — | ❌ **Tabla 4.2 (maestra de umbrales) no aparece en el repo** |
| 05 | Taxonomía de sistemas conversacionales | — | 📘 falta página propia |
| 06 | RAG | `02-ragas-basics/src/rag_pipeline.py` | 🟡 sin diagrama del pipeline, sin chunking |
| 07 | Métricas RAGAS | `02-ragas-basics` | ✅ |
| 08 | LLM-as-Judge | `03-llm-as-judge` | ✅ (G-Eval, DAG, position bias) |
| 09 | Golden Datasets | `goldens/*` | 🟡 **datasets <100 entradas; falta página guía** |
| 10 | Testing de chatbots (8 áreas: intent, fallback, escalation…) | — | ❌ no hay módulo dedicado |
| 11 | Evaluación semántica y similitud | `14-embedding-eval` | ✅ |
| 12 | Robustness y perturbation testing | `07-redteam-garak/src/robustness_suite.py` | 🟡 mezclado con red-team; manual los separa |
| 13 | Deriva semántica | `13-drift-monitoring` | ✅ KS test, bootstrap, AlertHistory |
| 14 | OWASP LLM Top 10 (2025) | `08-redteam-deepteam` | ✅ los 10 cubiertos |
| 15 | Prompt Injection (taxonomía ortogonal 3 ejes) | `08-redteam-deepteam/src/injection_classifier.py` | ✅ |
| 16 | Multi-turno y contexto | `04-multi-turn` | ✅ 7 métricas |
| 17 | Alucinaciones (taxonomía 2 niveles Ji et al.) | `06-hallucination-lab/src/hallucination_types.py` | ✅ |
| 18 | CI/CD y quality gates | `05-prompt-regression/src/ci_gate_pipeline.py` + `.github/workflows/evals.yml` | ✅ |
| 19 | Observabilidad (trace schema 20 campos) | `12-observability` | ✅ |
| 20 | Herramientas RAGAS/TruLens/DeepEval | `02`, `01` | 🟡 **no hay módulo TruLens ni comparativa** |
| 21 | Agentes y multi-agente | `10-agent-testing` | ✅ 9 métricas, AgentPolicy |
| 22 | Antipatrones de evaluación | `01-primer-eval/src/eval_antipatterns.py` | ✅ |
| 23 | Estrategia integral (madurez L1–L5) | — | ❌ falta página guía |
| 24 | Prompt Regression Testing | `05-prompt-regression` | ✅ |
| 25 | Bias, Toxicity y Safety | `08-redteam-deepteam/src/safety_suite.py` | 🟡 falta `evaluate_false_refusals` explícito y `false_refusal_rate` como métrica |
| 26 | Antipatrones operativos (OP-01..OP-10) | — | ❌ no implementado |
| 27 | **Cost-aware QA** | — | ❌ **gap crítico** — no hay módulo, ni `CostReport`, ni `assert_cost_budget` |
| 28 | Privacy y PII leakage | `09-guardrails/src/pii_canary.py` | ✅ |
| 29 | **Retrieval avanzado** (HyDE, hybrid, reranking) | — | ❌ no implementado |
| 30 | Function calling y tool use | `10-agent-testing/src/agent_policy.py::validate_tool_call` | 🟡 falta `CreateTicketMock`, escenarios `duplicate/rate_limited/invalid_args` |
| 31 | **Human-in-the-loop e IAA** | `03-llm-as-judge/src/judge_bias.py::cohen_kappa` | 🟡 falta Krippendorff α, ICC, protocolo de calibración |
| 32 | Reproducibilidad y determinismo | — | 📘 falta guía transversal (el patrón sí existe en `05/variance_evaluator.py`) |
| 33 | Glosario consolidado | `docs/glosario.md` + `site/guia/conceptos.md` | 🟡 **desactualizado**: faltan ~20 términos del Cap. 33 |
| App. A | 45 preguntas de consolidación | — | ❌ no aprovechado (podrían ser un `quiz/` interactivo en el site) |
| App. B | Referencias bibliográficas | — | ❌ no recogidas |
| App. C | Índice alfabético | — | ❌ no recogido |
| App. D | **Caso práctico end-to-end (chatbot seguros)** | — | ❌ **gap crítico** — sería un módulo `15-end-to-end-case` perfecto |

**Resumen numérico:**

- ✅ totalmente cubiertos: **17** capítulos
- 🟡 parciales: **10** capítulos
- ❌ no cubiertos: **6** capítulos + **4** apéndices
- 📘 faltan páginas conceptuales en el site: **4** capítulos

---

## 2. Errores y desincronías concretas

### 2.1 Marketing del repo (alta visibilidad, fácil de arreglar)

| # | Lugar | Texto actual | Realidad | Acción |
|---|---|---|---|---|
| E-01 | `README.md` línea 3 | `382 tests` | `grep -c "def test_" → 402` | actualizar a `402 tests` (o medir con `pytest --collect-only`) |
| E-02 | `site/index.md:48,60` | `382 passed` y `~0.9s` | igual | sincronizar con E-01 |
| E-03 | `site/index.md:7` | "Sin API key. Sin conexión." | cierto sólo con `-m "not slow"` | añadir matiz como el README |
| E-04 | `README.md` Stack | lista TruLens, Phoenix, NeMo, Promptfoo | ninguno tiene módulo dedicado | o crear módulos o quitarlos del stack |
| E-05 | `.github/workflows/redteam-nightly.yml` y `promptfoo.yml` | `schedule:` comentado | tareas nightly anunciadas en docs no se ejecutan | re-activar cron o documentar que están en pausa |

### 2.2 Desalineación con el manual v13 (autoridad rota)

| # | Manual v13 | Repo | Impacto |
|---|---|---|---|
| D-01 | Tabla 4.2 (umbrales mínimo / objetivo / alto riesgo) es la **única tabla maestra** referenciada por 12 capítulos | No existe como tabla central en ningún sitio del repo | tests usan umbrales hardcoded sin trazabilidad al manual |
| D-02 | §9.2: golden dataset ≥100 ejemplos para regression, 500–1000 robusto, 100+ por segmento crítico | Todos los `goldens/*.jsonl` tienen 8–15 entradas | los goldens del repo no pasarían su propio gate si se aplicara el manual |
| D-03 | §22 AP-04: "Confundir faithfulness con factual accuracy" | El módulo 02 mide solo faithfulness; no expone `AnswerCorrectness` con GT | falta una métrica explícita; el manual lo marca como antipatrón |
| D-04 | §25.4: medir `refusal_rate` y `false_refusal_rate` juntos | El repo tiene `run_safety_suite` pero no calcula `false_refusal_rate` como métrica separada | gate de safety sub-óptimo |
| D-05 | §32.4: patrón canónico = mediana sobre N=3–5 runs con IC95 | `05-prompt-regression/src/variance_evaluator.py::evaluate_with_variance` lo hace, pero no se aplica a los otros 13 módulos | el resto del repo trata stochastic como determinista |
| D-06 | §21.4: "execution trace" reemplaza a "reasoning trace" | El glosario del repo todavía habla de "reasoning trace" en lenguaje suelto | terminología obsoleta |
| D-07 | Cap. 33 lista ~50 términos canónicos | `docs/glosario.md` tiene ~30 | desfase del 40 % |
| D-08 | §4.7 reglas de escritura: prosa con acentos, código sin acentos, decimales con coma en prosa y punto en código | Páginas del site mezclan ambos estilos sin política | inconsistencia editorial |

### 2.3 Bugs detectados leyendo código + manual

| # | Archivo | Hallazgo |
|---|---|---|
| B-01 | `09-guardrails/src/pii_canary.py` | usa `raise PIILeakageError`, alineado con §28.4 (correcto) — pero el README dice que el módulo "detecta PII" sin mencionar que en runtime debe ser `raise`, no `assert`. Documentar mejor. |
| B-02 | `12-observability/src/trace_record.py` | falta el campo `system_fingerprint` que el manual incorpora en §32.5 como obligatorio para detectar snapshot drift |
| B-03 | `13-drift-monitoring/src/semantic_drift_detector.py` | el manual §13.3 ya recoge esta versión robusta (bootstrap + KS de dos muestras). Solo falta el aviso de `historical_scores.size >= 30` que sí existe en el código — perfecto, ningún cambio necesario aquí |
| B-04 | `10-agent-testing/src/agent_policy.py` | `validate_tool_call` no activa `FormatChecker` por defecto (§30.3 lo marca como **importante**: `jsonschema.validate()` no valida `format: email/date-time` sin `FormatChecker` explícito) — verificar y corregir si falta |
| B-05 | `08-redteam-deepteam/src/owasp_scenarios.py` | la taxonomía OWASP 2025 está completa, pero el manual §14.3 ahora desglosa LLM04 Data/Model Poisoning en 8 controles (preventivos + detectivos). El módulo lo trata como un único escenario binario. |

---

## 3. Plan de mejoras priorizado

### Prioridad 1 — alto impacto / esfuerzo medio (1–2 semanas)

1. **Crear módulo `15-cost-aware-qa`** (Cap. 27)
   - `CostReport` dataclass, `assert_cost_budget`, `PRICE_PER_1K` externalizado a config
   - 7 métricas: tokens in/out, USD/query, P50/P95/P99, TTFT, tool fan-out, retry rate
   - Gate `cost_delta ≤ +10 %` que se integre con `05-prompt-regression`

2. **Crear módulo `16-retrieval-advanced`** (Cap. 29)
   - HyDE, query rewriting, multi-query, hybrid (BM25+denso), reranking, parent-child, sentence-window, Self-RAG
   - Tests con `ranx` para NDCG@k antes y después de cada técnica
   - Gate "HyDE solo justifica su coste si ΔNDCG@5 ≥ +0.05"

3. **Añadir la Tabla 4.2 como página canónica**
   - `site/guia/umbrales.md` con la tabla maestra y los tres niveles
   - Sustituir hardcoded `0.85`, `0.70`… en módulos por imports de un `thresholds.py` central
   - Bonus: test que falla si un módulo usa un umbral no documentado en la tabla maestra

4. **Inflar los golden datasets a ≥100 por módulo**
   - Usar el agente `golden-generator` que ya existe en CLAUDE.md
   - Estratificar por categoría (cobertura, exclusión, ambiguo, fuera de dominio) según §9.2
   - Documentar IAA simulado y ratio sintético/real (§9.4: 70/30 → 30/70)

### Prioridad 2 — gaps conceptuales del site (1 semana)

5. **Página `site/guia/marco-normativo.md`** (Cap. 3)
   - EU AI Act categorías + obligaciones por nivel
   - ISO 25010 mapeada a métricas operativas del repo
   - Model card / system card / DPIA

6. **Página `site/guia/madurez.md`** (Cap. 23)
   - Modelo L1–L5 con checklist por nivel
   - Checklist de release (Tabla 23.2) accionable

7. **Página `site/guia/reproducibilidad.md`** (Cap. 32)
   - Las 4 fuentes de no-determinismo + mitigaciones
   - Patrón canónico mediana N runs + IC95
   - Anti-patrones de reproducibilidad

8. **Actualizar `docs/glosario.md` y `site/guia/conceptos.md`**
   - Añadir los 20 términos faltantes del Cap. 33
   - Eliminar "reasoning trace", sustituir por "execution trace"

### Prioridad 3 — capítulos que merecen su propio módulo (2 semanas)

9. **Módulo `17-chatbot-testing`** (Cap. 10)
   - 8 áreas operativas: intent, fallback, escalation, tono, memoria, aislamiento de sesiones, contexto largo, recuperación de errores
   - Diferencia explícita testing manual vs automatizado

10. **Módulo `18-robustness-suite`** (Cap. 12) o extraer de `07`
    - Separar perturbation testing de red teaming (el manual los trata distinto)
    - 8 categorías de perturbación: léxica, morfológica, sintáctica, léxico-semántica, idiomática, longitud, mayúsculas, adversarial sutil

11. **Módulo `19-hitl-iaa`** (Cap. 31)
    - Cohen κ, Krippendorff α, ICC
    - Protocolo de calibración 6 fases
    - Tests con anotaciones simuladas

### Prioridad 4 — apéndices del manual como contenido derivado

12. **Apéndice D → módulo `20-end-to-end-case`** (caso aseguradora salud)
    - Reproducir el incidente simulado (faithfulness cae de 0.91 a 0.76)
    - Triage runbook + postmortem
    - **Pieza estrella del repo**: es lo único en el manual que ata todos los capítulos

13. **Apéndice A → `site/quiz/` con 45 preguntas**
    - Quiz interactivo VitePress con respuestas reveladas
    - Filtrable por área (RAG, Safety, Bias, Agents...)
    - Excelente para SEO y captura de leads

14. **Apéndice B → `site/referencias.md`**
    - Lista curada de papers con enlaces verificados

### Prioridad 5 — limpieza y consistencia

15. Corregir los errores marcados E-01..E-05 (5 min)
16. Reactivar o documentar pausa de los crons `redteam-nightly.yml` y `promptfoo.yml`
17. Hook pre-commit que verifique que `pytest --collect-only` coincide con el número anunciado en README/site

---

## 4. Estado del site VitePress

Estructura actual: 7 guías + 14 páginas de módulos + index = 22 páginas. Páginas de módulos bien dimensionadas (150–250 líneas cada una).

**Lo que falta para alinearse con el manual:**
- 4 páginas de guía conceptual (Cap. 2, 5, 23, 32) que no existen.
- Página `guia/umbrales.md` con la Tabla 4.2 (crítica).
- Página `guia/golden-datasets.md` (Cap. 9 es entero teórico).
- Sección `guia/marco-normativo.md` (Cap. 3).
- Quiz interactivo (Apéndice A).
- Sección `caso-practico.md` (Apéndice D).

Después de estas adiciones, el site pasaría de 22 a ~32 páginas y representaría >90 % del manual.

---

## 5. Porcentaje de completitud (resumen)

| Dimensión | Estado |
|---|---|
| Implementación técnica de los conceptos del manual | **72 %** |
| Site documentation alineado con el manual | **64 %** |
| Golden datasets que cumplen el manual (§9.2) | **0 %** (todos <100) |
| Marketing/branding sincronizado con la realidad técnica | **80 %** (números desactualizados) |
| **Estimación global de "manual v13 implementado en el repo"** | **~70 %** |

Para llegar al **95 %**, las prioridades 1–4 son suficientes (≈ 4–6 semanas de trabajo).

---

## 6. Recomendaciones tácticas inmediatas (esta semana)

1. **Hoy:** corregir E-01 (`382 → 402` en README y site).
2. **Mañana:** crear `site/guia/umbrales.md` con la Tabla 4.2. Es la pieza que más se cita en el manual y no aparece en el repo.
3. **Esta semana:** decidir si Cost-aware (Cap. 27) y Retrieval avanzado (Cap. 29) entran como módulos 15 y 16 o como secciones de los existentes.
4. **Antes del próximo release:** ejecutar `golden-generator` sobre los 14 módulos para llegar a 100+ ejemplos por dataset.

---

*Auditoría generada automáticamente leyendo las 114 páginas del manual y cruzando con la estructura real del repo (modules/, site/, goldens/, .github/workflows/). Para regenerar: ver `audits/` y los agentes `module-creator`, `golden-generator`, `content-sync`, `ux-site` definidos en `CLAUDE.md`.*
