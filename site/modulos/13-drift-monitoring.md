---
title: "13 — drift-monitoring"
---

# 13 — drift-monitoring

Detectar degradación de calidad en producción con PSI, AlertHistory y reglas de alerta.

<div class="module-layout">
<div class="module-main">

## Qué aprenderás

- PSI (Population Stability Index): cuándo la distribución de scores ha cambiado significativamente
- `AlertHistory`: rastrear tendencias a lo largo del tiempo (degrading / recovering / stable)
- Reglas de alerta: mean drop, p95, PSI threshold configurable
- Cómo combinar varias reglas con `evaluate_rules()`

## Código de ejemplo

```python
from src.drift_detector import compute_psi
from src.alert_rules import AlertHistory, mean_drop_alert, psi_alert, evaluate_rules

psi = compute_psi(scores_referencia, scores_actuales)

rules = [
    mean_drop_alert(reference_mean=0.85, threshold_pct=0.1),
    psi_alert(threshold=0.2),
]
results = evaluate_rules(rules, scores_actuales)

history = AlertHistory("calidad_global")
for result in results:
    history.add(result)

print(history.trend)        # "degrading", "recovering" o "stable"
print(history.trigger_rate) # fracción de checks que activaron alerta
```

## Interpretación del PSI

| PSI | Interpretación |
|-----|---------------|
| < 0.1 | Sin cambio significativo |
| 0.1 – 0.2 | Cambio moderado, investigar |
| > 0.2 | Cambio significativo, actuar |

## Por qué importa

> En producción, los LLMs se degradan silenciosamente. Sin monitorización, lo detectas cuando los usuarios se quejan.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">16</div>
  <div class="stat-label">tests</div>
</div>

<div class="stat-card">
  <div class="stat-number">0.09s</div>
  <div class="stat-label">duración</div>
</div>

<div class="stat-card stat-ok">
  <div class="stat-number">✓</div>
  <div class="stat-label">sin API key</div>
</div>

<div class="stat-card">
  <div class="stat-number level">Avanzado</div>
  <div class="stat-label">nivel</div>
</div>

```bash
pytest modules/13-drift-monitoring/tests/ \
  -m "not slow" -q
```

<div class="module-next">
  <div class="next-label">Siguiente →</div>
  <a href="/modulos/14-embedding-eval">14 — embedding-eval</a>
</div>

</div>
</div>
