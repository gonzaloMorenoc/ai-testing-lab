---
title: "13 — drift-monitoring"
---

# 13 — drift-monitoring

Detectar degradación de calidad en producción con PSI, AlertHistory y reglas de alerta.

<div class="module-layout">
<div class="module-main">

## El problema

El modelo no ha cambiado. Los prompts tampoco. Pero los usuarios se quejan de peor calidad. Esto es drift: la distribución de las queries de entrada ha cambiado y el modelo ya no responde igual de bien. PSI mide cuánto ha cambiado esa distribución. Sin monitorización, una degradación silenciosa puede durar semanas antes de que lleguen suficientes quejas para detectarla.

## Cómo funciona

- **PSI (Population Stability Index):** compara la distribución de scores entre un período de referencia y el actual. Divide el rango en bins y calcula la divergencia.
  - PSI < 0.1: sin cambio significativo
  - 0.1–0.2: cambio moderado, investigar
  - > 0.2: cambio significativo, actuar
- **`AlertHistory`:** registra resultados de cada evaluación. Calcula tendencias: `degrading` (≥2 de los últimos 3 activaron alerta), `recovering` (0 de los últimos 3 activaron alerta), `stable` (exactamente 1 de los últimos 3).
- **`evaluate_rules`:** aplica múltiples reglas (`mean_drop_alert`, `p95_alert`) sobre una lista de scores.

```text
scores_referencia + scores_actuales → compute_psi → PSI value
evaluate_rules([mean_drop_alert, p95_alert], scores) → [AlertResult]
AlertResult → AlertHistory.add() → trend / trigger_rate
```

## Código paso a paso

**1. Calcular PSI e interpretar el valor**

`compute_psi` toma dos listas de scores (referencia y actual) y devuelve un float. Un valor por encima de 0.2 indica que la distribución ha cambiado de forma significativa.

```python
from src.drift_detector import compute_psi

scores_referencia = [0.85, 0.87, 0.83, 0.86, 0.84, 0.88, 0.85, 0.82, 0.87, 0.86]
scores_actuales   = [0.72, 0.70, 0.68, 0.71, 0.73, 0.69, 0.70, 0.72, 0.68, 0.71]

psi = compute_psi(scores_referencia, scores_actuales)
print(f"PSI = {psi:.4f}")
# PSI > 0.2 → cambio significativo, actuar
```

**2. Definir reglas y ejecutar `evaluate_rules`**

`mean_drop_alert` dispara si la media actual cae más de un porcentaje sobre la media de referencia. `evaluate_rules` aplica todas las reglas y devuelve una lista de `AlertResult`.

```python
from src.alert_rules import mean_drop_alert, p95_alert, evaluate_rules

rules = [
    mean_drop_alert(reference_mean=0.85, threshold_pct=0.1),
    p95_alert(limit=0.90),
]
results = evaluate_rules(rules, scores_actuales)

for r in results:
    print(r.rule_name, r.triggered, r.message)
```

**3. Rastrear tendencias con `AlertHistory`**

`AlertHistory` acumula los resultados y calcula si el sistema está mejorando, empeorando o estable.

```python
from src.alert_rules import AlertHistory

history = AlertHistory("calidad_global")
for result in results:
    history.add(result)

print(history.trend)        # "degrading", "recovering", "stable" o "insufficient_data"
print(history.trigger_rate) # fracción de checks que activaron alerta
```

## Técnicas avanzadas

El módulo incluye también `SemanticDriftDetector` en `src/semantic_drift_detector.py`, que combina el test de Kolmogorov-Smirnov de dos muestras con bootstrap IC95. A diferencia del PSI, que compara contra una referencia fija, el KS compara directamente las dos distribuciones — es más robusto frente a referencias tipo delta de Dirac y proporciona un intervalo de confianza sobre la magnitud del drift.

Para conectar los resultados de `AlertHistory` con Langfuse o Prometheus, exporta `trigger_rate` y `trend` como métricas estructuradas y envíalas al sistema de visualización en cada ciclo de monitorización.

## Errores comunes

- **PSI sin período de referencia establecido.** Cualquier comparación es arbitraria. Definir explícitamente qué ventana temporal es el baseline.
- **Alertar en el primer PSI > 0.2.** Puede ser un pico puntual. Usar `AlertHistory` para confirmar tendencia antes de actuar.
- **Una sola regla de alerta.** No distingue si el problema es la media o la distribución. Combinar `mean_drop_alert` y `p95_alert`.
- **No actualizar el baseline periódicamente.** El baseline queda obsoleto. Rotar el baseline mensualmente o tras deployments.

## En producción

| PSI | Acción recomendada |
|-----|-------------------|
| < 0.10 | Ninguna — monitorización normal |
| 0.10–0.20 | Investigar — posible cambio en inputs |
| > 0.20 | Actuar — evaluar reentrenamiento |

```bash
# scheduled en CI
pytest modules/13-drift-monitoring/tests/ -m "not slow" -q
```

Para instrumentar el pipeline que genera estos scores, ver módulo 12.

## Caso real en producción

Un retailer con chatbot de recomendaciones vio cómo, en campaña de Navidad, las queries cambiaron drásticamente: más urgencia, menos comparativas. PSI subió a 0.31 en la primera semana de diciembre. `AlertHistory` marcó tendencia `degrading` tras tres evaluaciones consecutivas. El equipo activó un modelo de respaldo entrenado con datos de campañas anteriores. Sin monitorización, habrían detectado el problema solo a través de quejas de usuarios.

## Ejercicios

- 🟢 Genera dos distribuciones de scores similares (ruido ±0.05) y calcula PSI. Verifica el archivo de test en `modules/13-drift-monitoring/tests/test_psi_alerts.py` y ejecuta `pytest modules/13-drift-monitoring/tests/ -m "not slow" -q`. ¿El PSI supera 0.1?
- 🟡 Implementa una secuencia de 6 evaluaciones donde las primeras 3 disparan alerta y las últimas 3 no. Verifica que `AlertHistory.trend` es `"recovering"`.
- 🔴 Diseña un sistema de monitorización con 30 días de datos simulados con degradación progresiva. Usa `evaluate_rules` y `AlertHistory` para detectar el punto exacto en que el sistema debería haber alertado.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">31</div>
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
