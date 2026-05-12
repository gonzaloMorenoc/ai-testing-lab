---
title: "20 — end-to-end-case"
---

# 20 — end-to-end-case

Caso práctico completo del Apéndice D del manual. **El único módulo que ata todos los capítulos** del manual en un flujo realista: contexto del producto → riesgos → métricas → gates → incidente → postmortem → release.

Si los 19 módulos anteriores muestran "cómo se hace cada pieza", este muestra "cómo encajan todas".

## El producto del caso (D.1)

Chatbot interno para una aseguradora médica.

| Atributo | Valor |
|---|---|
| Usuarios | 800 asesores |
| Países | España, Portugal, Reino Unido (ES/PT/EN) |
| Volumen | ~25 000 queries/día, picos × 4 |
| Stack | Claude Sonnet 4.5 (LLM principal) + Haiku 4.5 (clasificación) + embeddings multilingües + reranker |
| Corpus | 12 000 documentos normativos |
| Equipo | 1 TechLead, 2 Backend, 1 ML Engineer, 1 QA Engineer, 2 Domain Experts (legal y clínico), 1 Security Lead compartido |

## Riesgos → requisitos (D.1)

Seis riesgos canónicos. Cada uno con un requisito de QA verificable:

| Riesgo | Impacto | Requisito de QA |
|---|---|---|
| Hallucination | Reclamación legal | Faithfulness ≥ 0.90 + Answer Correctness ≥ 0.88 |
| PII leak | Sanción RGPD/HIPAA | 0 leaks en suite de canary tokens y PII probes |
| Prompt injection | Acción no autorizada | Suite OWASP LLM01:2025 con payloads directos e indirectos |
| Language bias | Servicio desigual | Kruskal-Wallis p > 0.01 y \|Δ\| ≤ 0.05 entre idiomas |
| Uncontrolled cost | Sobrecoste mensual | Cost regression Δ ≤ +10 %; tool fan-out ≤ 5 |
| Low robustness | UX degradada | Consistency mean ≥ 0.80 sobre perturbaciones |

## El incidente (D.8): faithfulness cae de 0.91 a 0.76

::: warning Lo que ocurrió
El release **v3.2** introdujo un cambio de tono en el prompt que degradó la cita textual de coberturas, aumentando alucinaciones extrínsecas. Faithfulness cae de **0.91 → 0.76** y refusal rate de **0.99 → 0.93** sobre las queries de cobertura.

**Causa raíz**: el gate de PR de faithfulness (≥0.85) estaba inadvertidamente desactivado tras un merge conflictivo en `.github/workflows/qa-gate.yml`. Antipatrones combinados: **AP-10** (no versionar configuración de gates) + **OP-09** (métricas sin baseline activa).
:::

### Línea de tiempo del runbook

```text
T+0 ──── PagerDuty firing: faithfulness < 0.80 sustained 15 min
T+5 ──── Tech Lead compara versiones; bisección apunta al prompt
T+15 ─── Regression suite (Cap. 24) muestra Δ faithfulness = -0.15
         Investigación: el gate de PR estaba desactivado tras merge
         conflictivo. AP-10 + OP-09 confirmados.
T+25 ─── Rollback al prompt v3.1 vía MLflow + Git
         Faithfulness vuelve a 0.90
T+40 ─── Feature flag bloquea v3.2 para todos los usuarios
         Postmortem agendado
```

## La lección estructural (D.10)

> La cobertura de tests no protege si el sistema de gates se rompe en silencio. Añadir meta-tests al pipeline y tratar el fichero de workflow como código de producción versionado y revisado.

Las cinco mejoras estructurales acordadas:

1. **Meta-test en CI** que falla si faltan gates obligatorios en el workflow.
2. **Versionado obligatorio del prompt** con changelog firmado por QA Lead.
3. **Alertas dobles**: por umbral absoluto y por drift estadístico.
4. **Auditoría trimestral** del checklist de release con revisor externo.
5. **Robustness suite en PR** también para idiomas minoritarios.

## Release v3.3: decisión final (D.11)

Tras la remediación, v3.3 cierra el ciclo en T+14d:

| Métrica | Observado | Umbral | Pasa |
|---|:---:|:---:|:---:|
| Faithfulness | 0.93 | ≥ 0.90 | ✓ |
| Consistency robustness | 0.84 | ≥ 0.80 | ✓ |
| Refusal rate | 0.99 | ≥ 0.99 | ✓ |
| PII canary leaks | 0 | = 0 | ✓ |
| Cost vs baseline | +3 % | ≤ +10 % | ✓ |

Aprobado por QA Engineer + Domain Experts. Canary al 5 % durante 48 h antes de full rollout.

## Cómo se reproduce desde código

```python
from gates_pipeline import Stage, evaluate_stage
from incident_simulator import reproduce_incident, should_trigger_alert

incident = reproduce_incident()
# {'prompt_version_pre': 'v3.1', 'prompt_version_incident': 'v3.2',
#  'faithfulness_pre': 0.91, 'faithfulness_post': 0.76,
#  'delta_faithfulness': -0.15, ...}

# v3.2 habría sido bloqueado si los gates hubieran estado activos
observed_v3_2 = {
    "faithfulness": incident["faithfulness_post"],
    "answer_correctness": 0.80,
    "context_recall": 0.85,
    "ndcg_at_5": 0.82,
    "safety_canary_leaks": 0.0,
}
result = evaluate_stage(Stage.PRE_STAGING, observed_v3_2)
assert not result.passed  # gate bloquea correctamente
```

## Conexión con todos los módulos

| Pieza del caso | Módulo del repo |
|---|---|
| Faithfulness, context recall | [02 — ragas-basics](./02-ragas-basics) |
| Tabla 4.2 umbrales | [Tabla maestra](../guia/umbrales) |
| OWASP LLM | [08 — redteam-deepteam](./08-redteam-deepteam) |
| Canary tokens + PII | [09 — guardrails](./09-guardrails) |
| Drift y alertas dobles | [13 — drift-monitoring](./13-drift-monitoring) |
| Cost regression | [15 — cost-aware-qa](./15-cost-aware-qa) |
| NDCG@5 retrieval | [16 — retrieval-advanced](./16-retrieval-advanced) |
| Chatbot operativo | [17 — chatbot-testing](./17-chatbot-testing) |
| Robustness por idioma | [18 — robustness-suite](./18-robustness-suite) |
| IAA del dataset (α ≥ 0.80) | [19 — hitl-iaa](./19-hitl-iaa) |

## Referencias

- Manual QA AI v13 — Apéndice D (pp. 110–114), Figura D.1
- Cap. 23 — Estrategia integral, Tabla 23.2 (checklist de release multi-equipo)
- Caps. 22 + 26 — Antipatrones (AP-10, OP-09)
