# Módulo 08 — Red Team con DeepTeam

**Status:** planned

## Objetivos

- Automatizar el OWASP Top 10 para LLM con DeepTeam de DeepEval
- Usar PyRIT de Microsoft para generar ataques adversariales de forma programática
- Ejecutar ataques Crescendo multi-turno para evadir defensas mediante escalada gradual

## Capítulo del manual

Este módulo cubre los conceptos de la sección X del manual (`docs/06-red-teaming-y-owasp.md`).

## Conceptos clave

- DeepTeam: red teaming integrado con el ecosistema DeepEval
- OWASP Top 10 LLM automatizado: prompt injection, insecure output handling, data leakage
- PyRIT (Python Risk Identification Toolkit): framework de Microsoft para ataques automatizados
- Crescendo multi-turn: técnica de escalada gradual para evadir guardrails

## Cómo ejecutar (pendiente)

```bash
# Disponible cuando el módulo esté implementado
cd modules/08-redteam-deepteam
uv sync --extra redteam
pytest tests/
```

## Ejercicio propuesto (pendiente)

_Descripción del ejercicio que se añadirá cuando se implemente el módulo._

## Estructura

```
08-redteam-deepteam/
├── README.md
├── src/          # código del lab (pendiente)
└── tests/        # tests del lab (pendiente)
```
