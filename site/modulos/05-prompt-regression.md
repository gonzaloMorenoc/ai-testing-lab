# 05 — prompt-regression

**Concepto:** Detectar regresiones de calidad cuando cambias un prompt. Significación estadística.

**Tests:** 11 · **Tiempo:** ~0.05s · **API key:** no necesaria

## Qué aprenderás

- `PromptRegistry`: versionar prompts como código con hash
- `RegressionChecker`: comparar dos versiones de un prompt sobre el mismo dataset
- z-test de una proporción para saber si la diferencia es estadísticamente significativa
- Cuándo una mejora del 3% importa y cuándo no

## Ejecutar

```bash
pytest modules/05-prompt-regression/tests/ -m "not slow" -q
```

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

Sin test estadístico, una mejora del 2% con 20 muestras parece real pero puede ser ruido. Un z-test te dice si necesitas más datos o si el resultado es conclusivo.
