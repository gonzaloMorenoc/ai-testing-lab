# 13 — drift-monitoring

**Concepto:** Detectar degradación de calidad en producción con PSI, AlertHistory y reglas de alerta.

**Tests:** 13 · **Tiempo:** ~0.05s · **API key:** no necesaria

## Qué aprenderás

- PSI (Population Stability Index): cuándo la distribución de scores ha cambiado significativamente
- `AlertHistory`: rastrear tendencias a lo largo del tiempo (degrading / recovering / stable)
- Reglas de alerta: mean drop, p95, PSI threshold configurable
- Cómo combinar varias reglas con `evaluate_rules()`

## Ejecutar

```bash
pytest modules/13-drift-monitoring/tests/ -m "not slow" -q
```

## Código de ejemplo

```python
from src.drift_detector import compute_psi
from src.alert_rules import AlertHistory, mean_drop_alert, psi_alert, evaluate_rules

# PSI entre distribución de referencia y actual
psi = compute_psi(scores_referencia, scores_actuales)

# Reglas de alerta
rules = [
    mean_drop_alert(reference_mean=0.85, threshold_pct=0.1),
    psi_alert(threshold=0.2),
]
results = evaluate_rules(rules, scores_actuales)

# Historial de tendencias
history = AlertHistory("calidad_global")
for result in results:
    history.add(result)

print(history.trend)         # "degrading", "recovering" o "stable"
print(history.trigger_rate)  # fracción de checks que activaron alerta
print(history.summary())
```

## Interpretación del PSI

| PSI | Interpretación |
|-----|---------------|
| < 0.1 | Sin cambio significativo |
| 0.1 – 0.2 | Cambio moderado, investigar |
| > 0.2 | Cambio significativo, actuar |
