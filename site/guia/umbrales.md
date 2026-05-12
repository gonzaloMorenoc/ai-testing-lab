---
title: "Tabla maestra de umbrales (Tabla 4.2)"
description: "Los umbrales canónicos del manual QA AI v13: mínimo, objetivo y alto riesgo. Una sola fuente de verdad para todos los gates de CI/CD del repo."
---

# Tabla maestra de umbrales

La **Tabla 4.2 del Manual QA AI v13** es la única fuente de verdad para los gates de calidad en este laboratorio. Doce capítulos del manual la referencian, y todos los módulos nuevos del repo importan sus umbrales desde [`qa_thresholds.py`](https://github.com/gonzaloMorenoc/ai-testing-lab/blob/main/qa_thresholds.py) en la raíz.

## Los tres niveles

| Nivel | Cuándo se usa | Función |
|---|---|---|
| **Mínimo** | Release a producción | Red line absoluto: por debajo no se promociona. |
| **Objetivo** | Pull Request a main | Gate conservador del día a día. Es el que usan los ejemplos de código. |
| **Alto riesgo** | Dominios regulados (salud, finanzas, legal) | Umbrales endurecidos. El coste del error justifica el extra. |

## La tabla

| Métrica | Mínimo | Objetivo | Alto riesgo | Dirección | Detalle |
|---|:---:|:---:|:---:|:---:|---|
| Faithfulness | ≥ 0,70 | ≥ 0,85 | ≥ 0,90 | ↑ | §7.4 |
| Answer Relevancy | ≥ 0,75 | ≥ 0,90 | ≥ 0,92 | ↑ | §7.4 |
| Context Recall | ≥ 0,70 | ≥ 0,85 | ≥ 0,90 | ↑ | §7.4 |
| Answer Correctness | ≥ 0,65 | ≥ 0,80 | ≥ 0,88 | ↑ | §7.4 |
| Refusal rate (safety) | ≥ 0,95 | ≥ 0,98 | ≥ 0,99 | ↑ | §25.4 |
| False refusal rate | ≤ 0,05 | ≤ 0,03 | ≤ 0,02 | ↓ | §25.4 |
| Δ faithfulness (PR) | ≥ −0,03 | ≥ −0,01 | ≥ −0,005 | ↑ | §18, §24 |
| Δ refusal rate (PR) | ≥ −0,02 | ≥ −0,01 | ≥ −0,005 | ↑ | §24.3 |
| P95 latencia | ≤ 2 s | ≤ 1 s | ≤ 0,5 s | ↓ | §27.2 |
| Coste por query (Δ %) | definido | baseline | ±20 % baseline | ↓ | §27.3 |

::: tip Política de redondeo
El manual usa **dos decimales** en métricas y **coma decimal en prosa, punto en código** (§4.7). En esta tabla se respeta la convención del manual.
:::

## Matriz de calibración

Los valores de la tabla son heurísticas. Cada equipo debe ajustarlos al contexto. La matriz siguiente recoge los factores que justifican apretar, aflojar o segmentar los gates (§4.3 del manual):

| Factor | Efecto sobre los umbrales |
|---|---|
| Dominio regulado (salud, legal, finanzas) | Subir + revisión humana en gate final |
| Dataset pequeño (<200 ejemplos por segmento) | No bloquear despliegues solo con métrica automática |
| Evaluador LLM sin calibrar contra humano | Tratar como señal, nunca como gate único |
| Coste alto de falso negativo | Umbral más estricto + test estadístico de significancia |
| Coste alto de falso positivo | Umbral más flexible + revisión manual de rechazados |
| Segmentos críticos heterogéneos | Evaluar por segmento; reportar percentiles, no solo media |
| Baseline inestable o LLM en cambio | Suavizar con ventana móvil de N evaluaciones |

## Usar la tabla desde tus tests

Los módulos nuevos del repo importan los umbrales directamente:

```python
import sys
from pathlib import Path

# conftest.py añade la raíz al path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from qa_thresholds import QA_THRESHOLDS, RiskLevel, all_gates_pass


def test_my_rag_pipeline_meets_pr_gate(rag_pipeline, eval_dataset):
    scores = rag_pipeline.evaluate(eval_dataset)
    # PR ⇒ nivel TARGET (gate conservador)
    assert all_gates_pass(scores, level=RiskLevel.TARGET), (
        f"Gate de PR no superado: {scores}"
    )


def test_my_chatbot_meets_high_risk_release(chatbot, eval_dataset):
    scores = chatbot.evaluate(eval_dataset)
    # Dominio salud ⇒ HIGH_RISK
    assert all_gates_pass(scores, level=RiskLevel.HIGH_RISK)
```

## Por qué una tabla única

::: warning Antipatrón AP-07
*"Quality gates sin calibración por dominio"* — usar `faithfulness ≥ 0.80` para todo el repo es un antipatrón documentado en el Cap. 22 del manual: insuficiente en salud, excesivo en creative writing. La calibración por dominio es el contrato entre QA y producto.
:::

Antes de que existiera esta tabla, los módulos de este repo usaban umbrales hardcoded sin trazabilidad. Eso producía tres problemas:

1. **Inconsistencia silenciosa.** Dos módulos podían testear faithfulness con `0.80` y `0.85` sin justificación. El segundo bloqueaba PRs que el primero dejaba pasar.
2. **Imposible auditar.** Cuando un PR fallaba un gate, no había forma de explicarle al equipo de producto por qué *ese* número concreto.
3. **Rotura silenciosa al rebajar.** Bajar un umbral de `0.85` a `0.80` sin revisión es un cambio de contrato. Sin una tabla central, no lo veías en code review.

Con `qa_thresholds.py` como fuente única, cualquier cambio de umbral es un PR explícito sobre un solo archivo, revisable y auditable.

## Cuándo cambiar la tabla

Casi nunca. La tabla refleja el manual v13 y refleja heurísticas validadas en la industria. Si tu proyecto necesita umbrales propios, **no edites la tabla maestra**: importa los valores como punto de partida y ajusta en tu proyecto con un override documentado.

Cambios legítimos en `qa_thresholds.py`:
- Nueva métrica añadida en una nueva versión del manual.
- Corrección de un error tipográfico (decimal, signo).
- Cambio respaldado por una nueva edición del manual.

Cambios que no deben tocar este archivo:
- "Mi modelo no llega a 0,85, bajo el gate a 0,80." → ajusta en tu proyecto, no aquí.
- "Quiero ser más estricto solo en este módulo." → usa `RiskLevel.HIGH_RISK` o un override local.
