---
title: "06 — hallucination-lab"
---

# 06 — hallucination-lab

Detectar alucinaciones a nivel de claim individual. Groundedness con detección de negaciones.

<div class="module-layout">
<div class="module-main">

## Qué aprenderás

- Extracción de claims: descomponer una respuesta en afirmaciones verificables
- Groundedness: ¿cada claim está respaldado por el contexto?
- Detección de negaciones: "las devoluciones NO están permitidas" contradice el contexto
- La diferencia entre alucinación (información inventada) y contradicción (negar lo que dice el contexto)

## Código de ejemplo

```python
from src.groundedness_checker import GroundednessChecker

checker = GroundednessChecker(overlap_threshold=0.4)
context = "Las devoluciones están permitidas en 30 días."

# Claim que contradice el contexto
assert not checker.is_grounded(
    "Las devoluciones NO están permitidas.", context
)

# Claim respaldado por el contexto
assert checker.is_grounded(
    "Se puede devolver en 30 días.", context
)
```

## Nuevas implementaciones (Manual QA AI v12)

**`HallucinationClassifier`** — taxonomía de 2 niveles (Ji et al. 2023, Cap 14):

```python
from src.hallucination_types import HallucinationClassifier, HallucinationLevel1, HallucinationLevel2

classifier = HallucinationClassifier()
report = classifier.classify(
    response="Napoleon ganó la batalla de Waterloo en 1815.",
    context="En Waterloo (1815), Napoleon fue derrotado.",
    unsupported_claims=["Napoleon ganó"],
)
# report.level1 = HallucinationLevel1.INTRINSIC  (contradice el contexto)
# report.level2 = HallucinationLevel2.FACTUAL    (hecho factual incorrecto)
# report.confidence: float, report.explanation: str
```

| Nivel 1 | Nivel 2 |
|---------|---------|
| `INTRINSIC` — contradice el contexto | `FACTUAL` — hecho factual incorrecto |
| `EXTRINSIC` — información no verificable | `TEMPORAL` — dato temporal erróneo |
| | `NUMERICAL` — cifra inventada |
| | `CITATION` — referencia inexistente |
| | `LOGICAL` — inconsistencia interna |

## Por qué importa

> La mayoría de métricas de faithfulness no detectan negaciones explícitas. Un modelo que dice "No tienes derecho a devoluciones" cuando el contexto dice que sí las hay pasa los filtros de overlap léxico estándar.

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
