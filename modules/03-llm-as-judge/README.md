# Módulo 03 — LLM as Judge

**Status:** planned

## Objetivos

- Implementar el patrón G-Eval usando un LLM como evaluador automatizado
- Diseñar rúbricas custom para evaluar calidad, coherencia y relevancia de respuestas
- Identificar y mitigar los sesgos inherentes al LLM-as-judge (position bias, verbosity bias)

## Capítulo del manual

Este módulo cubre los conceptos de la sección X del manual (`docs/03-metricas.md`).

## Conceptos clave

- G-Eval: evaluación guiada por cadena de pensamiento con LLM
- LLM como evaluador: ventajas frente a métricas automáticas clásicas
- Sesgos del juez LLM: position bias, verbosity bias, self-enhancement bias
- Rúbricas custom y DAG Metric para evaluaciones compuestas

## Cómo ejecutar (pendiente)

```bash
# Disponible cuando el módulo esté implementado
cd modules/03-llm-as-judge
uv sync --extra judge
pytest tests/
```

## Ejercicio propuesto (pendiente)

_Descripción del ejercicio que se añadirá cuando se implemente el módulo._

## Estructura

```
03-llm-as-judge/
├── README.md
├── src/          # código del lab (pendiente)
└── tests/        # tests del lab (pendiente)
```
