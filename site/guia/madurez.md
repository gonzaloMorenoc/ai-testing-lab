---
title: "Modelo de madurez QA AI: L1 → L5"
description: "Los cinco niveles de madurez de un programa de QA AI. Dónde estás, qué te falta para subir, y qué módulos del repo cubren cada nivel."
---

# Modelo de madurez QA AI

Construir un programa de QA AI no se hace de un día para otro. El Cap. 23 del manual v13 define un modelo de cinco niveles, desde el ad-hoc inicial hasta la excelencia automatizada. Cada nivel tiene un objetivo concreto y una checklist accionable.

## Los cinco niveles

| Nivel | Características | Objetivo del nivel siguiente |
|---|---|---|
| **L1 · Ad-hoc** | Tests manuales puntuales, sin framework | Pasar a evaluación reproducible |
| **L2 · Inicial** | Golden dataset básico, métricas manuales | Automatizar evaluación offline |
| **L3 · Gestionado** | CI/CD integrado, quality gates básicos | Monitorización en producción |
| **L4 · Optimizado** | Monitorización continua, deriva detectada, robustness suite | Mejora continua basada en datos |
| **L5 · Excelencia** | Evaluación multi-dimensional, automatización completa de QA | QA proactiva y predictiva |

::: tip Cómo se usa
Localiza tu equipo en la tabla. El nivel siguiente es la **dirección**, no la meta a corto plazo: pasar de L2 a L3 toma ~1–2 trimestres en equipos pequeños; de L3 a L4, ~2–4 trimestres.
:::

## L1 → L2: de ad-hoc a inicial

Cuando arrancas, lo único que tienes es un Slack lleno de capturas y una hoja Excel con "outputs raros". La transición a L2 es la más rápida y la más rentable.

**Checklist L1 → L2:**

- [ ] Golden dataset versionado en `goldens/` (mínimo 100 ejemplos, §9.2).
- [ ] Métrica baseline registrada para cada release.
- [ ] Tests automatizados con pytest (cualquier módulo del repo sirve como referencia).
- [ ] Un único punto de evaluación reproducible (`pytest modules/01-primer-eval/tests/ -q`).

Módulos del repo que te llevan a L2:
- [01 — primer-eval](../modulos/01-primer-eval): tu primer `LLMTestCase` con métricas deterministas.
- [09 — Golden Datasets](https://github.com/gonzaloMorenoc/ai-testing-lab/tree/main/goldens): formato JSONL canónico.

## L2 → L3: de inicial a gestionado

El salto de L2 a L3 es **integración con CI/CD**. Hasta L2 evalúas a mano; en L3, cada PR pasa por gates automáticos.

**Checklist L2 → L3:**

- [ ] CI workflow ejecutando la suite en cada PR.
- [ ] Quality gates con umbrales de la [Tabla 4.2](./umbrales).
- [ ] Versionado de prompts (`PromptRegistry`).
- [ ] Logging estructurado de cada request en producción.
- [ ] Regression testing automatizado contra baseline.

Módulos del repo:
- [05 — prompt-regression](../modulos/05-prompt-regression): `CIGatePipeline` + `PromptRegistry`.
- [02 — ragas-basics](../modulos/02-ragas-basics): métricas RAGAS en CI.
- [18 (manual) — CI/CD](https://github.com/gonzaloMorenoc/ai-testing-lab/blob/main/.github/workflows/evals.yml): GitHub Actions de referencia.

## L3 → L4: de gestionado a optimizado

L4 introduce la dimensión **producción**: ya no solo evalúas pre-deploy, sino que **monitorizas continuamente** la calidad de las respuestas reales.

**Checklist L3 → L4:**

- [ ] Pipeline de monitorización continua (sampling de producción → métricas online).
- [ ] Detector de drift configurado (KS-test + bootstrap IC95).
- [ ] Robustness suite ejecutándose en nightly.
- [ ] Suite OWASP LLM Top 10 en CI nightly.
- [ ] Dashboards con métricas online (Grafana/Langfuse).
- [ ] Alerting automático con PagerDuty/Slack.
- [ ] IAA medido trimestralmente sobre revisiones humanas.

Módulos del repo:
- [12 — observability](../modulos/12-observability): trace schema y collector.
- [13 — drift-monitoring](../modulos/13-drift-monitoring): KS-test + AlertHistory.
- [07 — redteam-garak](../modulos/07-redteam-garak): perturbaciones para robustness.
- [08 — redteam-deepteam](../modulos/08-redteam-deepteam): OWASP suite.

## L4 → L5: de optimizado a excelencia

L5 es la frontera. Pocos equipos están en L5. Características distintivas: evaluación multi-dimensional automatizada, eval-driven development (los evals dictan qué cambiar en el sistema), y predicción de degradación antes de que ocurra.

**Checklist L4 → L5:**

- [ ] Cobertura ≥ 95 % de los caminos críticos del sistema con tests automatizados.
- [ ] Causal analysis: cuando una métrica baja, el sistema apunta automáticamente al componente responsable (modelo, prompt, retriever, corpus).
- [ ] Predicción de drift antes de que ocurra (análisis de tendencias).
- [ ] Tests de coste, latencia y calidad ponderados en una métrica única de release readiness.
- [ ] HITL solo en casos de muy bajo confidence, no en muestreo aleatorio.
- [ ] Re-anotación automática del golden set cuando el dominio evoluciona.

Módulos del repo (parcialmente L5):
- [15 — cost-aware-qa](../modulos/15-cost-aware-qa): tests de coste como métrica de primer orden.
- [16 — retrieval-advanced](../modulos/16-retrieval-advanced): gate ΔNDCG@5 que decide qué técnica entra.

## Arquitectura de la estrategia de QA (todas las capas)

Un sistema en L4–L5 opera sobre cinco capas simultáneas:

```text
┌──────────────────────────────────────────────────────────┐
│ Capa humana                                              │
│   ↳ Revisión manual de casos escalados                   │
│   ↳ Calibración de umbrales · auditorías periódicas      │
├──────────────────────────────────────────────────────────┤
│ Capa de robustness                                       │
│   ↳ Batería de perturbaciones por dominio (Cap. 12)      │
├──────────────────────────────────────────────────────────┤
│ Capa de costes                                           │
│   ↳ Token tracking · coste por query · budgets (Cap. 27) │
├──────────────────────────────────────────────────────────┤
│ Capa online                                              │
│   ↳ Sampling de producción · drift · alertas (Cap. 13)   │
├──────────────────────────────────────────────────────────┤
│ Capa offline                                             │
│   ↳ Golden datasets · RAGAS · regression (Cap. 7, 24)    │
└──────────────────────────────────────────────────────────┘
```

## Checklist de release multi-equipo (Tabla 23.2)

El checklist canónico antes de promocionar una release a producción. Cada item con un responsable y una herramienta:

| Ítem | Criterio de éxito | Herramienta | Responsable |
|---|---|---|---|
| Eval suite completa | Pass rate ≥ 95 % en golden | RAGAS / DeepEval | QA Engineer |
| Regression test | Δ faithfulness ≥ −0.03 vs baseline | DeepEval CI | QA Engineer |
| Robustness suite | Consistency mean ≥ 0.80 | PromptBench / custom | QA Engineer |
| Security scan | 0 vulnerabilidades críticas | OWASP LLM / Manual | Security Lead |
| Privacy / PII test | 0 leaks en canary tokens | Custom (Cap. 28) | Security Lead |
| Drift baseline | Similarity baseline con IC95 documentada | Custom detector | MLOps |
| Cost budget | Coste/query dentro de presupuesto | LangSmith / Langfuse | FinOps |
| Quality gates CI | Todos los gates en verde | GitHub Actions | DevOps |
| Human review | 50 casos revisados por experto de dominio | LabelStudio / Argilla | Domain Expert |
| Rollback plan | Rollback a versión anterior documentado | MLflow / Git | Tech Lead |
| Monitoring ready | Dashboards y alertas configurados | Grafana / Langfuse | MLOps |

## Caso típico: subir de L2 a L4 en seis meses

Patrón observado en equipos pequeños (3–6 personas):

**Mes 1–2 (L2 → L3):**
- Golden dataset estable y versionado.
- Pipeline CI con un único gate (faithfulness ≥ 0.85 objetivo).
- `PromptRegistry` configurado.

**Mes 3–4 (L3 → L3.5):**
- Suite RAGAS completa en CI.
- Logging estructurado con `request_id` y `prompt_version`.
- Quality gates por etapa: PR / staging / pre-prod / canary.

**Mes 4–5 (L3.5 → L4):**
- Detector de drift activo sobre `golden_v2`.
- Suite OWASP nightly.
- Dashboard básico con faithfulness P50/P95.

**Mes 5–6 (consolidar L4):**
- Robustness suite en nightly por idioma.
- Cost-aware tests en CI (Δ ≤ +10 %).
- Calibración trimestral de umbrales.

::: tip Realismo
Pasar de L2 a L4 en seis meses requiere dedicación parcial de un QA Engineer + buy-in del equipo. Sin esto, el plan se diluye. La señal de que vas por buen camino: cada release tarda menos en evaluarse y los falsos positivos del CI bajan.
:::

## Antipatrones de madurez

- **Saltarse niveles.** "Implementamos L5 directamente." Los gates fallan por falta de baseline; las alertas son ruido porque no hay calibración.
- **Confundir tooling con madurez.** Comprar Langfuse no te lleva a L4 si nadie mira los dashboards.
- **Métrica única.** Equipos en L3 que reportan solo `pass rate` están ciegos a coste, latencia y robustness.
- **Tests sin owner.** Suites en CI que llevan meses fallando porque "ya hablamos con el equipo X". L3 real requiere ownership.

## Referencias

- Manual QA AI v13 — Cap. 23 (Estrategia integral de QA AI), Tablas 23.1 y 23.2
- [Tabla maestra de umbrales](./umbrales)
- ISO/IEC 42001:2023 — AI Management Systems
