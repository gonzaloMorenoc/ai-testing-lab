# Módulo 06 — Hallucination Lab

**Status:** planned

## Objetivos

- Detectar alucinaciones con `HallucinationMetric` y `FaithfulnessMetric` de DeepEval
- Aplicar el RAG Triad de TruLens para evaluar groundedness, relevancia de contexto y relevancia de respuesta
- Construir un conjunto de test cases diseñados para provocar y detectar alucinaciones

## Capítulo del manual

Este módulo cubre los conceptos de la sección X del manual (`docs/02-tipos-de-testing.md` y `docs/03-metricas.md`).

## Conceptos clave

- HallucinationMetric: detección de información fabricada no respaldada por el contexto
- FaithfulnessMetric: fidelidad de la respuesta a los documentos recuperados
- RAG Triad (TruLens): groundedness, context relevance, answer relevance
- Técnicas para provocar alucinaciones y construir datasets de evaluación adversarial

## Cómo ejecutar (pendiente)

```bash
# Disponible cuando el módulo esté implementado
cd modules/06-hallucination-lab
uv sync --extra eval
pytest tests/
```

## Ejercicio propuesto (pendiente)

_Descripción del ejercicio que se añadirá cuando se implemente el módulo._

## Estructura

```
06-hallucination-lab/
├── README.md
├── src/          # código del lab (pendiente)
└── tests/        # tests del lab (pendiente)
```
