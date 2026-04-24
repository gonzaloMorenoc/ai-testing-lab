# Módulo 02 — RAGAS Basics

**Status:** planned

## Objetivos

- Comprender el framework RAGAS y sus métricas principales para evaluar pipelines RAG
- Aplicar las métricas `faithfulness`, `answer_relevancy`, `context_precision` y `context_recall`
- Ejecutar evaluaciones reference-free sobre un pipeline RAG de ejemplo

## Capítulo del manual

Este módulo cubre los conceptos de la sección X del manual (`docs/03-metricas.md` y `docs/04-frameworks-oss.md`).

## Conceptos clave

- RAGAS framework y su filosofía de evaluación sin referencia
- Métricas RAG: faithfulness, answer_relevancy, context_precision, context_recall
- Reference-free evaluation vs reference-based evaluation
- Estructura y componentes de un pipeline RAG evaluable

## Cómo ejecutar (pendiente)

```bash
# Disponible cuando el módulo esté implementado
cd modules/02-ragas-basics
uv sync --extra eval
pytest tests/
```

## Ejercicio propuesto (pendiente)

_Descripción del ejercicio que se añadirá cuando se implemente el módulo._

## Estructura

```
02-ragas-basics/
├── README.md
├── src/          # código del lab (pendiente)
└── tests/        # tests del lab (pendiente)
```
