---
title: "05 — prompt-regression"
---

# 05 — prompt-regression

Detectar regresiones de calidad cuando cambias un prompt. Significación estadística con z-test.

<div class="module-layout">
<div class="module-main">

## Qué aprenderás

- `PromptRegistry`: versionar prompts como código con hash
- `RegressionChecker`: comparar dos versiones de un prompt sobre el mismo dataset
- z-test de una proporción para saber si la diferencia es estadísticamente significativa
- Cuándo una mejora del 3% importa y cuándo no

## Código de ejemplo

```python
from src.regression_checker import RegressionChecker, is_significant

checker = RegressionChecker()
delta = checker.compare(baseline_scores, candidate_scores)

if is_significant(delta, n_samples=200, baseline_score=0.75):
    print(f"Mejora real: +{delta:.1%}")
else:
    print("Diferencia dentro del ruido estadístico")
```

## Por qué importa

> Sin test estadístico, una mejora del 2% con 20 muestras parece real pero puede ser ruido. Un z-test te dice si necesitas más datos o si el resultado es conclusivo.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">18</div>
  <div class="stat-label">tests</div>
</div>

<div class="stat-card">
  <div class="stat-number">0.06s</div>
  <div class="stat-label">duración</div>
</div>

<div class="stat-card stat-ok">
  <div class="stat-number">✓</div>
  <div class="stat-label">sin API key</div>
</div>

<div class="stat-card">
  <div class="stat-number level">Intermedio</div>
  <div class="stat-label">nivel</div>
</div>

```bash
pytest modules/05-prompt-regression/tests/ \
  -m "not slow" -q
```

<div class="module-next">
  <div class="next-label">Siguiente →</div>
  <a href="/modulos/06-hallucination-lab">06 — hallucination-lab</a>
</div>

</div>
</div>
