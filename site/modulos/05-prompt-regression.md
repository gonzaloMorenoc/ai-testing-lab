---
title: "05 — prompt-regression"
---

# 05 — prompt-regression

Detectar regresiones de calidad cuando cambias un prompt. Significación estadística con z-test.

<div class="module-layout">
<div class="module-main">

## El problema

Cambias un prompt, los resultados parecen mejores. El score medio sube del 0.81 al 0.84. ¿Es una mejora real o ruido estadístico? Con 20 muestras, una diferencia del 3% puede ser completamente aleatoria. Sin test estadístico, cada cambio de prompt es una apuesta. Con regresión de prompts, cada cambio tiene un veredicto objetivo: mejora real, regresión detectada, o diferencia dentro del ruido.

## Cómo funciona

`PromptRegistry` almacena cada versión de un prompt con su hash SHA-256. Permite reproducir cualquier versión anterior. `RegressionChecker` compara los scores del baseline con los del candidato sobre el mismo dataset. La función `is_significant` aplica un z-test de una proporción: con n=200 y baseline=0.75, una diferencia de 0.03 tiene p-value ~0.04 — significativa. Con n=20, la misma diferencia tiene p-value ~0.35 — ruido.

```text
prompt_v1 → scores_baseline
prompt_v2 → scores_candidato
        ↓
RegressionChecker → delta
        ↓
is_significant(delta, n, baseline) → veredicto
```

Bootstrap IC95 evalúa el modelo N veces (N_RUNS=5) para estimar la varianza real. Temperatura=0 no garantiza determinismo.

## Código paso a paso

**Paso 1 — Registrar dos versiones de prompt con `PromptRegistry`**

```python
from src.prompt_registry import PromptRegistry, PromptVersion

registry = PromptRegistry()

registry.register(PromptVersion(
    name="support_response",
    version="v1",
    template="You are a support agent. Answer: {question}",
    description="Prompt básico sin instrucciones de formato",
))

registry.register(PromptVersion(
    name="support_response",
    version="v2",
    template=(
        "You are a helpful customer support agent. "
        "Answer concisely and accurately, "
        "citing policy details when relevant: {question}"
    ),
    description="Prompt mejorado con instrucciones de formato",
))

v1 = registry.get("support_response", "v1")
v2 = registry.get("support_response", "v2")
print(registry.list_versions("support_response"))  # ['v1', 'v2']
```

**Paso 2 — Comparar scores con `RegressionChecker` y aplicar `is_significant`**

```python
from src.regression_checker import RegressionChecker, is_significant

checker = RegressionChecker(threshold=0.03)
report = checker.check(
    prompt_name="support_response",
    baseline_version="v1",
    baseline_score=0.81,
    candidate_version="v2",
    candidate_score=0.84,
    metric_name="faithfulness",
)
print(report.summary())
# [OK] support_response: v1=0.81 → v2=0.84 (▲0.03)

# ¿La diferencia de 0.03 es significativa?
sig_20 = is_significant(delta=0.03, n_samples=20, baseline_score=0.81)
sig_200 = is_significant(delta=0.03, n_samples=200, baseline_score=0.81)
print(sig_20)   # False — ruido con 20 muestras
print(sig_200)  # True  — señal real con 200 muestras
```

**Paso 3 — Usar `evaluate_with_variance` para bootstrap IC95**

```python
from src.variance_evaluator import evaluate_with_variance

# N_RUNS=5 en PR, evaluaciones reales del modelo
report = evaluate_with_variance(
    scores=[0.82, 0.85, 0.83, 0.81, 0.84],
    expected_threshold=0.80,
    metric="faithfulness",
)
print(report.median)      # 0.83
print(report.ci95_low)    # límite inferior del IC95
print(report.ci95_high)   # límite superior del IC95
print(report.passed)      # True si mediana >= 0.80 y ci_low >= 0.78
```

## Técnicas avanzadas

**`VarianceEvaluator` con bootstrap IC95.** Temperatura=0 no es determinista — el mismo prompt puede dar scores distintos en ejecuciones diferentes. Bootstrap IC95 te da el rango real de varianza en lugar de un único punto, lo que es especialmente importante antes de decidir si mergear una PR de cambio de prompt.

```python
from src.variance_evaluator import compare_pairwise, REGRESSION_THRESHOLDS

# Compara baseline vs candidato sobre varias métricas simultáneamente
regression = compare_pairwise(
    baseline={"faithfulness": 0.85, "answer_relevancy": 0.90},
    candidate={"faithfulness": 0.81, "answer_relevancy": 0.88},
)
print(regression.delta)
# {"faithfulness": -0.04, "answer_relevancy": -0.02}
print(regression.failing_metrics)
# ["faithfulness"]  — delta -0.04 < umbral -0.03
print(regression.regression)
# True
```

**`CIGatePipeline` con thresholds escalonados.** En un pipeline de CI con múltiples entornos, necesitas gates distintos por etapa: más permisivo en PR donde quieres iterar rápido, más estricto en producción donde el coste de un error es alto.

```python
from src.ci_gate_pipeline import CIGatePipeline, CIStage

pipeline = CIGatePipeline()

# Gate de PR: umbrales mínimos
pr_result = pipeline.run_gate(
    CIStage.PR,
    scores={"faithfulness": 0.82, "answer_relevancy": 0.88},
    baseline={"faithfulness": 0.85, "answer_relevancy": 0.90},
)
print(pr_result.passed)  # True — deltas dentro del umbral PR

# Pipeline completo: identifica dónde falla
first_fail = pipeline.first_failing_stage(
    scores={"faithfulness": 0.84, "answer_relevancy": 0.87},
    baseline={"faithfulness": 0.85, "answer_relevancy": 0.90},
)
print(first_fail)  # CIStage.CANARY — pasa PR y Staging pero falla Canary
```

| Etapa      | Faithfulness | Relevancy | Delta máx |
|------------|-------------|-----------|-----------|
| PR         | ≥ 0.70      | ≥ 0.75    | −0.03     |
| Staging    | ≥ 0.80      | ≥ 0.85    | −0.02     |
| Canary     | ≥ 0.85      | ≥ 0.88    | −0.01     |
| Production | ≥ 0.90      | ≥ 0.92    | −0.01     |

## Errores comunes

- **Comparar mejoras con muestras < 30.** Con n=20 una diferencia del 3% no es estadísticamente significativa. Usar mínimo 30 casos, recomendado 100-200.
- **Asumir que temperatura=0 es reproducible.** Los modelos tienen varianza interna. Siempre ejecutar N_RUNS≥3 y calcular IC95 en lugar de un único punto.
- **Usar el mismo dataset para desarrollar y evaluar el prompt.** El data leakage infla artificialmente los scores. Separar dataset de desarrollo y de evaluación.
- **Gate único para todos los entornos.** Un único threshold es demasiado estricto en PR (bloquea iteración) o demasiado laxo en producción (permite regresiones). Usar `CIGatePipeline` con thresholds escalonados.

## En producción

Los gates de CI se configuran por etapa. El comando estándar para la suite completa es:

```bash
pytest modules/05-prompt-regression/tests/ -m "not slow" -q
```

| Etapa      | Faithfulness | Relevancy | Delta máx |
|------------|-------------|-----------|-----------|
| PR         | ≥ 0.70      | ≥ 0.75    | −0.03     |
| Staging    | ≥ 0.80      | ≥ 0.85    | −0.02     |
| Canary     | ≥ 0.85      | ≥ 0.88    | −0.01     |
| Production | ≥ 0.90      | ≥ 0.92    | −0.01     |

Integrar `CIGatePipeline` en el paso de validación del CI: si `first_failing_stage` devuelve un valor distinto de `None`, el pipeline falla y el PR no se mergea.

## Caso real en producción

Un SaaS B2B de atención al cliente iteraba el prompt del chatbot cada sprint. Tras 4 sprints consecutivos de "mejoras", el score en staging era 0.83 — pero la IC95 calculada con `evaluate_with_variance` era [0.79, 0.87]. El equipo se dio cuenta de que ninguna de las 4 iteraciones había producido una mejora estadísticamente significativa: el límite inferior del IC95 nunca superó el target de la etapa anterior.

Implementaron `CIGatePipeline` y establecieron una regla clara: un PR solo se mergea si el IC95 inferior supera el target de la etapa en curso. En el sprint siguiente, la primera iteración con un cambio real de instrucciones produjo IC95 = [0.83, 0.89] y mergeó sin discusión.

## Ejercicios

🟢 **Significación según tamaño de muestra.** Ejecuta `is_significant` con n=20, n=50 y n=200 para la misma diferencia de 0.03 y baseline=0.75. Los tests de referencia están en `modules/05-prompt-regression/tests/test_regression.py`. Ejecuta:

```bash
pytest modules/05-prompt-regression/tests/ -m "not slow" -q
```

¿A partir de qué tamaño de muestra la diferencia es significativa?

🟡 **Comparación de versiones con `PromptRegistry`.** Implementa un `PromptRegistry` con dos versiones de un prompt de soporte al cliente y compara sus scores con `RegressionChecker`. Usa `compare_pairwise` para evaluar faithfulness y answer_relevancy simultáneamente. Documenta qué versión gana y con qué nivel de confianza.

🔴 **Pipeline CI con `CIGatePipeline`.** Simula un pipeline completo donde los scores pasan PR (faithfulness=0.84, relevancy=0.87) y Staging pero fallan en Canary porque el delta de faithfulness supera −0.01. Verifica que `first_failing_stage` devuelve `CIStage.CANARY`. El archivo de test de referencia es `modules/05-prompt-regression/tests/test_ci_gate_pipeline.py`.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">43</div>
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
