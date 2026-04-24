# Módulo 05 — Prompt Regression

**Status:** planned

## Objetivos

- Usar Promptfoo para evaluar matrices de prompts contra múltiples modelos simultáneamente
- Comparar baseline vs candidato de forma automatizada y reproducible
- Integrar evaluaciones de prompt regression en un GitHub Action con caché eficiente

## Capítulo del manual

Este módulo cubre los conceptos de la sección X del manual (`docs/02-tipos-de-testing.md` y `docs/08-ci-cd.md`).

## Conceptos clave

- Promptfoo: herramienta de evaluación prompts×modelos en matriz
- Regresión de prompts: detectar degradaciones entre versiones de prompt
- Comparación baseline vs candidato con métricas cuantitativas
- GitHub Action con caché para evitar re-evaluar prompts sin cambios

## Cómo ejecutar (pendiente)

```bash
# Disponible cuando el módulo esté implementado
cd modules/05-prompt-regression
uv sync --extra regression
pytest tests/
```

## Ejercicio propuesto (pendiente)

_Descripción del ejercicio que se añadirá cuando se implemente el módulo._

## Estructura

```
05-prompt-regression/
├── README.md
├── src/          # código del lab (pendiente)
└── tests/        # tests del lab (pendiente)
```
