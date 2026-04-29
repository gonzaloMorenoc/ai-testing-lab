# 06 — hallucination-lab

**Concepto:** Detectar alucinaciones a nivel de claim individual. Groundedness con detección de negaciones.

**Tests:** 9 · **Tiempo:** ~0.05s · **API key:** no necesaria

## Qué aprenderás

- Extracción de claims: descomponer una respuesta en afirmaciones verificables
- Groundedness: ¿cada claim está respaldado por el contexto?
- Detección de negaciones: "las devoluciones NO están permitidas" contradice el contexto
- La diferencia entre alucinación (información inventada) y contradicción (negar lo que dice el contexto)

## Ejecutar

```bash
pytest modules/06-hallucination-lab/tests/ -m "not slow" -q
```

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

## Por qué importa

La mayoría de métricas de faithfulness no detectan negaciones explícitas. Un modelo que dice "No tienes derecho a devoluciones" cuando el contexto dice que sí las hay pasa los filtros de overlap léxico estándar.
