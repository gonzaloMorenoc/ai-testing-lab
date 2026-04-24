# Módulo 12 — Observability

**Status:** planned

## Objetivos

- Instrumentar un pipeline RAG con Langfuse o Phoenix para tracing completo
- Configurar OpenTelemetry para capturar spans de cada paso del pipeline
- Implementar online evaluation sampling para evaluar respuestas en producción

## Capítulo del manual

Este módulo cubre los conceptos de la sección X del manual (`docs/12-tendencias.md`).

## Conceptos clave

- Langfuse: plataforma de observabilidad LLM con tracing, evaluaciones y datasets
- Phoenix (Arize): alternativa open-source para tracing y evaluación de pipelines LLM
- OpenTelemetry: estándar de observabilidad para instrumentar pipelines de forma portable
- Online evaluation sampling: evaluar un porcentaje de respuestas en producción de forma continua

## Cómo ejecutar (pendiente)

```bash
# Disponible cuando el módulo esté implementado
cd modules/12-observability
uv sync --extra observability
docker compose -f ../../docker/compose.yml up langfuse -d
pytest tests/
```

## Ejercicio propuesto (pendiente)

_Descripción del ejercicio que se añadirá cuando se implemente el módulo._

## Estructura

```
12-observability/
├── README.md
├── src/          # código del lab (pendiente)
└── tests/        # tests del lab (pendiente)
```
