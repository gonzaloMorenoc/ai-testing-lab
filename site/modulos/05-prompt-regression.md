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

## Nuevas implementaciones (Manual QA AI v12)

**`VarianceEvaluator`** — evalúa varianza entre runs y detecta regresiones con bootstrap IC95 (Cap 21 + Cap 29):

```python
from src.variance_evaluator import evaluate_with_variance, compare_pairwise, REGRESSION_THRESHOLDS

# N_RUNS=5 en PR, bootstrap IC95
report = evaluate_with_variance(
    scores=[0.82, 0.85, 0.83, 0.81, 0.84],
    expected_threshold=0.80,
)
# report.mean=0.83, report.ci95_low, report.ci95_high, report.passed=True

# Compara baseline vs candidato
regression = compare_pairwise(
    baseline={"faithfulness": 0.85, "answer_relevancy": 0.90},
    candidate={"faithfulness": 0.81, "answer_relevancy": 0.88},
)
# REGRESSION_THRESHOLDS = {"faithfulness": -0.03, ...}
# delta faithfulness = -0.04 < -0.03 → regresión detectada
```

`ACCEPTANCE_MARGIN = 0.02` — temperatura=0 **no** garantiza determinismo, siempre usa bootstrap.

**`CIGatePipeline`** — pipeline de quality gates por etapas (Cap 15):

```python
from src.ci_gate_pipeline import CIGatePipeline, CIStage

pipeline = CIGatePipeline()

# Gate de PR: umbrales mínimos, permite más tolerancia
result = pipeline.run_gate(
    CIStage.PR,
    scores={"faithfulness": 0.82, "answer_relevancy": 0.88},
    baseline={"faithfulness": 0.85, "answer_relevancy": 0.90},
)
# result.passed = True si scores OK y deltas dentro de umbral

# Pipeline completo: PR → Staging → Canary → Production
all_results = pipeline.run_all_stages(scores, baseline)
first_fail = pipeline.first_failing_stage(scores, baseline)
# first_fail = CIStage.CANARY si pasa PR y Staging pero falla Canary
```

| Etapa | Faithfulness | Relevancy | Delta máx. |
|-------|-------------|-----------|------------|
| PR | ≥ 0.70 | ≥ 0.75 | −0.03 |
| Staging | ≥ 0.80 | ≥ 0.85 | −0.02 |
| Canary | ≥ 0.85 | ≥ 0.88 | −0.01 |
| Production | ≥ 0.90 | ≥ 0.92 | −0.01 |

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
