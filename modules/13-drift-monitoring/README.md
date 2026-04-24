# Módulo 13 — Drift Monitoring

**Status:** planned

## Objetivos

- Detectar drift de input, output y concepto en pipelines LLM en producción
- Aplicar métricas estadísticas PSI y KS sobre distribuciones de embeddings
- Configurar alertas automáticas con Evidently AI cuando se detecta drift significativo

## Capítulo del manual

Este módulo cubre los conceptos de la sección X del manual (`docs/11-buenas-practicas.md` y `docs/12-tendencias.md`).

## Conceptos clave

- Input drift: cambio en la distribución de consultas de usuario con el tiempo
- Output drift: degradación en la calidad o distribución de respuestas del modelo
- Concept drift: cambio en la relación entre inputs y outputs esperados
- PSI (Population Stability Index) y KS (Kolmogorov-Smirnov) sobre embeddings
- Evidently AI: framework para monitorización de ML y LLM en producción

## Cómo ejecutar (pendiente)

```bash
# Disponible cuando el módulo esté implementado
cd modules/13-drift-monitoring
uv sync --extra monitoring
pytest tests/
```

## Ejercicio propuesto (pendiente)

_Descripción del ejercicio que se añadirá cuando se implemente el módulo._

## Estructura

```
13-drift-monitoring/
├── README.md
├── src/          # código del lab (pendiente)
└── tests/        # tests del lab (pendiente)
```
