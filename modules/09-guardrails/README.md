# Módulo 09 — Guardrails

**Status:** planned

## Objetivos

- Implementar rails de seguridad con NeMo Guardrails de NVIDIA para controlar el comportamiento del LLM
- Usar Guardrails AI para validar inputs y outputs con validators personalizados
- Prevenir PII leakage y temas prohibidos con topic rails y filtros semánticos

## Capítulo del manual

Este módulo cubre los conceptos de la sección X del manual (`docs/06-red-teaming-y-owasp.md`).

## Conceptos clave

- NeMo Guardrails: framework declarativo para controlar flujos conversacionales
- Guardrails AI: validators programáticos para inputs y outputs de LLM
- Topic rails: restricción de temas permitidos en la conversación
- PII leakage prevention: detección y redacción de información personal identificable

## Cómo ejecutar (pendiente)

```bash
# Disponible cuando el módulo esté implementado
cd modules/09-guardrails
uv sync --extra redteam
pytest tests/
```

## Ejercicio propuesto (pendiente)

_Descripción del ejercicio que se añadirá cuando se implemente el módulo._

## Estructura

```
09-guardrails/
├── README.md
├── src/          # código del lab (pendiente)
└── tests/        # tests del lab (pendiente)
```
