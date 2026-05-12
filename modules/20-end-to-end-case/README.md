# 20 — end-to-end-case (Apéndice D)

Caso práctico completo del Manual QA AI v13. Reproduce el ciclo entero de QA para un chatbot RAG en dominio regulado: contexto del producto → riesgos → métricas → gates → incidente → postmortem → release.

Es **el único módulo que ata todos los capítulos** del manual.

## Quickstart

```bash
pytest modules/20-end-to-end-case/tests/ -q
```

```
68 passed in 0.08s
```

## Qué cubre

Cada archivo del módulo refleja una sección concreta del Apéndice D:

| Archivo | Apéndice | Contenido |
|---|---|---|
| `product_setup.py` | D.1 | Contexto: chatbot interno aseguradora salud, 800 asesores, ES/PT/EN, 25k queries/día, Sonnet 4.5 + Haiku 4.5 |
| `risk_map.py` | D.1 | Tabla D.1: 6 riesgos → 6 requisitos de QA |
| `metrics_plan.py` | D.4 | Tabla D.2: plan de métricas por capa con frecuencia y umbrales |
| `gates_pipeline.py` | D.5 | 4 gates: PR / pre-staging / pre-prod / canary 1 % |
| `safety_suite.py` | D.6 | 60 payloads OWASP + 50 canary tokens + 200 PII probes |
| `incident_simulator.py` | D.8 | Línea de tiempo T+0 → T+40min del incidente faithfulness |
| `postmortem.py` | D.9, D.10 | Bug report estructurado + 5 mejoras estructurales |

## El incidente simulado (D.8)

El release v3.2 introdujo un cambio de tono que degradó la cita textual de coberturas, aumentando alucinaciones extrínsecas. Faithfulness cae de **0.91 → 0.76**, refusal rate de **0.99 → 0.93**.

El gate de PR de faithfulness (≥0.85) estaba inadvertidamente desactivado tras un merge conflictivo en `.github/workflows/qa-gate.yml`. Antipatrones combinados: **AP-10** (no versionar configuración de gates) + **OP-09** (métricas sin baseline activa).

### Línea de tiempo (reproducible con `INCIDENT_TIMELINE`)

| T+ | Acción | Faithfulness | Versión prompt |
|---:|---|---:|---|
| 0 | Alerta PagerDuty (sustained 15 min) | 0.76 | v3.2 |
| 5 | Comparar versiones; bisección apunta a prompt | 0.76 | v3.2 |
| 15 | Regression suite confirma Δ = -0.15 | 0.76 | v3.2 |
| 25 | Rollback a v3.1 vía MLflow + Git | 0.90 | v3.1 |
| 40 | Feature flag bloquea v3.2 | 0.91 | v3.1 |

### Las 5 mejoras estructurales (D.10)

1. **Meta-test en CI** que falle si faltan gates obligatorios en el workflow. Previene AP-10 + OP-09.
2. **Versionado obligatorio del prompt** con changelog firmado por QA Lead antes del merge.
3. **Alertas dobles**: por umbral absoluto y por drift estadístico (complementarias).
4. **Auditoría trimestral** del checklist de release (Tabla 23.2) con revisor externo.
5. **Robustness suite en PR** también para idiomas minoritarios (no solo nightly).

## Cómo se conecta con el resto del repo

| Componente del módulo 20 | Módulo origen |
|---|---|
| Métricas RAGAS (faithfulness, context recall) | [02 — ragas-basics](../02-ragas-basics/) |
| Gates de Tabla 4.2 | [`qa_thresholds.py`](../../qa_thresholds.py) raíz |
| Suite OWASP LLM | [08 — redteam-deepteam](../08-redteam-deepteam/) |
| Canary tokens y PII probes | [09 — guardrails](../09-guardrails/) |
| Drift y alertas dobles | [13 — drift-monitoring](../13-drift-monitoring/) |
| Cost regression | [15 — cost-aware-qa](../15-cost-aware-qa/) |
| NDCG@5 | [16 — retrieval-advanced](../16-retrieval-advanced/) |
| Robustness suite | [18 — robustness-suite](../18-robustness-suite/) |
| IAA del dataset (Krippendorff α ≥ 0.80) | [19 — hitl-iaa](../19-hitl-iaa/) |

## Cómo se reproduce el flujo completo

```python
from gates_pipeline import Stage, evaluate_stage
from incident_simulator import reproduce_incident, should_trigger_alert

# 1. Estado normal pre-incidente
observed = {"faithfulness": 0.91, "consistency": 0.84, "cost_delta": 0.02}
assert evaluate_stage(Stage.PULL_REQUEST, observed).passed

# 2. Incidente simulado
incident = reproduce_incident()
# Alerta dispara
assert should_trigger_alert(incident["faithfulness_post"], sustained_minutes=15)

# 3. v3.2 habría sido bloqueado si los gates hubieran estado activos
observed_v3_2 = {
    "faithfulness": 0.76,
    "answer_correctness": 0.80,
    "context_recall": 0.85,
    "ndcg_at_5": 0.82,
    "safety_canary_leaks": 0.0,
}
assert not evaluate_stage(Stage.PRE_STAGING, observed_v3_2).passed

# 4. Rollback + release v3.3 (con gates restaurados)
observed_v3_3 = {**observed_v3_2, "faithfulness": 0.93, "answer_correctness": 0.89}
assert evaluate_stage(Stage.PRE_STAGING, observed_v3_3).passed
```

## La lección estructural

Del manual §D.10:

> La cobertura de tests no protege si el sistema de gates se rompe en silencio. Añadir meta-tests al pipeline y tratar el fichero de workflow como código de producción versionado y revisado.

## Referencias

- Manual QA AI v13 — Apéndice D (pp. 110–114), Figura D.1 (línea de tiempo)
- Cap. 23 — Estrategia integral de QA AI (Tabla 23.2 checklist de release)
- Cap. 22 + 26 — Antipatrones de evaluación y operativos (AP-10 + OP-09)
- [Tabla maestra de umbrales](https://github.com/gonzaloMorenoc/ai-testing-lab/blob/main/qa_thresholds.py)
