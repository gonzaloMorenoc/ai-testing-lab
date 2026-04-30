---
title: "06 — hallucination-lab"
---

# 06 — hallucination-lab

Detectar alucinaciones a nivel de claim individual. Groundedness con detección de negaciones.

<div class="module-layout">
<div class="module-main">

## El problema

Las métricas de faithfulness estándar miden overlap léxico entre la respuesta y el contexto. No detectan negaciones: si el contexto dice "las devoluciones están permitidas en 30 días" y la respuesta dice "las devoluciones NO están permitidas", el overlap léxico sigue siendo alto. Tu modelo puede estar contradiciendo activamente al contexto y tus métricas lo pasan como correcto. Las alucinaciones más peligrosas no son las que inventan información — son las que la niegan.

## Cómo funciona

La respuesta se descompone en afirmaciones atómicas verificables (claims). Cada claim se compara con el contexto usando overlap léxico combinado con detección de negación. Un claim negado que contradice el contexto falla aunque tenga alta similitud léxica. Las palabras "no", "nunca", "jamás", "sin" invierten la polaridad del claim.

```text
respuesta → extracción de claims → [claim1, claim2, ...]
                                          ↓
                         groundedness_check(claim, contexto)
                                          ↓
                               [grounded / not_grounded]
```

La taxonomía Ji et al. 2023 clasifica alucinaciones en dos niveles ortogonales: nivel 1 (intrínseco vs extrínseco) y nivel 2 (factual, temporal, numérico, citation, lógico). Un claim intrínseco contradice el contexto; uno extrínseco añade información no verificable desde el contexto.

## Código paso a paso

**Paso 1 — Usar `GroundednessChecker` con un claim positivo que pasa**

```python
from src.groundedness_checker import GroundednessChecker

checker = GroundednessChecker(overlap_threshold=0.4)
context = "Las devoluciones están permitidas en 30 días."

# Claim respaldado por el contexto
result = checker.is_grounded("Se puede devolver en 30 días.", context)
print(result)  # True — overlap léxico suficiente, sin negación
```

**Paso 2 — Probar con un claim negado que falla**

```python
# Claim que contradice el contexto mediante negación
result = checker.is_grounded(
    "Las devoluciones NO están permitidas.", context
)
print(result)
# False — tokens positivos solapan con el contexto pero la negación los invierte

result2 = checker.is_grounded(
    "El envío nunca llega en 30 días.", context
)
print(result2)  # False — "nunca" activa la guardia de negación
```

**Paso 3 — Usar `HallucinationClassifier` para clasificar el tipo de alucinación**

```python
from src.hallucination_types import HallucinationClassifier

classifier = HallucinationClassifier()
report = classifier.classify(
    response="Napoleon ganó la batalla de Waterloo en 1815.",
    context="En Waterloo (1815), Napoleon fue derrotado.",
    unsupported_claims=["Napoleon ganó"],
)
print(report.level1)       # HallucinationLevel1.INTRINSIC
print(report.level2)       # HallucinationLevel2.FACTUAL
print(report.confidence)   # 0.8
print(report.has_hallucination)  # True
```

## Técnicas avanzadas

**`HallucinationClassifier` con taxonomía de dos niveles.** Saber que el modelo alucinó es el primer paso. Saber qué tipo de alucinación es te permite priorizar correcciones: una alucinación numérica en un contexto financiero tiene un impacto muy diferente a una alucinación de cita en contenido editorial. La clasificación permite escalar prioridades de forma sistemática en lugar de tratar todas las alucinaciones igual.

| Nivel 1     | Nivel 2    | Descripción                              |
|-------------|------------|------------------------------------------|
| `INTRINSIC` | `FACTUAL`  | Contradice un hecho del contexto         |
| `INTRINSIC` | `TEMPORAL` | Contradice una fecha o secuencia         |
| `INTRINSIC` | `NUMERICAL`| Contradice una cifra del contexto        |
| `INTRINSIC` | `LOGICAL`  | Conclusión inconsistente con el contexto |
| `EXTRINSIC` | `CITATION` | Referencia a fuente no presente          |
| `EXTRINSIC` | cualquiera | Información no verificable desde el contexto |

```python
from src.hallucination_types import (
    HallucinationClassifier,
    HallucinationLevel1,
    HallucinationLevel2,
)

classifier = HallucinationClassifier()

# Alucinación numérica intrínseca
report = classifier.classify(
    response="El descuento es del 100%.",
    context="El descuento máximo aplicable es del 20%.",
    unsupported_claims=["El descuento es del 100%"],
)
print(report.level1)  # INTRINSIC
print(report.level2)  # NUMERICAL — "100%" activa la señal numérica extrema
```

## Errores comunes

- **Usar solo faithfulness.** Las métricas de overlap no detectan negaciones ni contradicciones directas. Usar `GroundednessChecker` con detección de negación como capa adicional.
- **No distinguir intrínseco de extrínseco.** Las alucinaciones extrínsecas no siempre son errores — pueden ser información válida que el modelo añade desde su conocimiento paramétrico. Clasificar antes de decidir qué acción tomar.
- **Claims demasiado largos con varias afirmaciones.** Un claim que contiene varias ideas mezcla verdades y errores, haciendo imposible la evaluación atómica. Descomponer en afirmaciones de una sola idea antes de evaluar.
- **Solo testear claims positivos.** Si el test suite no incluye casos con "no", "nunca", "jamás", "sin", el detector de negación nunca se ejercita y las regresiones pasan desapercibidas.

## En producción

Priorizar la respuesta según el tipo de alucinación detectada:

```bash
pytest modules/06-hallucination-lab/tests/ -m "not slow" -q
```

| Tipo de alucinación      | Prioridad          |
|--------------------------|--------------------|
| INTRINSIC + FACTUAL      | Crítica — bloquear |
| INTRINSIC + NUMERICAL    | Alta — bloquear    |
| INTRINSIC + LOGICAL      | Alta — bloquear    |
| EXTRINSIC + cualquier    | Media — revisar    |

Para evaluar faithfulness a nivel de pipeline completo, ver módulo 02 — ragas-basics.

## Caso real en producción

Una plataforma de salud con chatbot de información sobre síntomas realizó una auditoría de respuestas. Encontraron casos donde el modelo decía "este síntoma NO requiere atención médica urgente" cuando el contexto clínico indicaba lo contrario. `FaithfulnessMetric` pasaba estos casos con scores de 0.71 porque el overlap léxico era alto — las palabras clave del contexto aparecían en la respuesta, simplemente precedidas por una negación.

`GroundednessChecker` con detección de negación marcó correctamente estos casos como `not_grounded`. El equipo añadió el checker al pipeline de validación de todas las respuestas antes de mostrarlas al usuario. La clasificación con `HallucinationClassifier` permitió enrutar los casos `INTRINSIC + FACTUAL` a revisión médica inmediata, separándolos de los casos `EXTRINSIC` que simplemente requerían revisión editorial.

## Ejercicios

🟢 **Detección de negación con `GroundednessChecker`.** Crea un caso donde la respuesta incluye la palabra "no" antes de un dato que sí aparece en el contexto. El archivo de test está en `modules/06-hallucination-lab/tests/test_hallucination.py`. Ejecuta:

```bash
pytest modules/06-hallucination-lab/tests/ -m "not slow" -q
```

¿Detecta `GroundednessChecker` la negación cuando el overlap léxico positivo es alto?

🟡 **Clasificación con `HallucinationClassifier`.** Construye un conjunto de 10 claims (5 correctos, 3 negados, 2 extrínsecos) y usa `HallucinationClassifier` para clasificar los incorrectos. ¿Qué patrones léxicos son más difíciles de detectar — los que usan negación explícita o los que usan eufemismos como "no necesariamente"?

🔴 **Integración con el pipeline del módulo 01.** Añade verificación de negación a un `LLMTestCase` del módulo 01 — primer-eval. Diseña un caso donde `AnswerRelevancy` pasa (la respuesta es relevante a la pregunta) pero `GroundednessChecker` falla (la respuesta niega información del contexto). Documenta el resultado con los dos scores en paralelo.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">23</div>
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
pytest modules/06-hallucination-lab/tests/ \
  -m "not slow" -q
```

<div class="module-next">
  <div class="next-label">Siguiente →</div>
  <a href="/modulos/07-redteam-garak">07 — redteam-garak</a>
</div>

</div>
</div>
