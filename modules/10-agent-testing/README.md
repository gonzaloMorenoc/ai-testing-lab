# Módulo 10 — Agent Testing

**Status:** planned

## Objetivos

- Evaluar agentes LLM con `ToolCallAccuracy` y `AgentGoalAccuracy` de DeepEval
- Analizar trayectorias de ejecución de agentes para detectar comportamientos incorrectos
- Aplicar las métricas de agentes de RAGAS para pipelines agenticos complejos

## Capítulo del manual

Este módulo cubre los conceptos de la sección X del manual (`docs/02-tipos-de-testing.md` y `docs/12-tendencias.md`).

## Conceptos clave

- ToolCallAccuracy: ¿el agente usa las herramientas correctas con los parámetros adecuados?
- AgentGoalAccuracy: ¿el agente cumple el objetivo especificado por el usuario?
- Trajectory evaluation: análisis paso a paso del razonamiento y acciones del agente
- RAGAS agent metrics: métricas específicas para pipelines agenticos y multi-step reasoning

## Cómo ejecutar (pendiente)

```bash
# Disponible cuando el módulo esté implementado
cd modules/10-agent-testing
uv sync --extra agents
pytest tests/
```

## Ejercicio propuesto (pendiente)

_Descripción del ejercicio que se añadirá cuando se implemente el módulo._

## Estructura

```
10-agent-testing/
├── README.md
├── src/          # código del lab (pendiente)
└── tests/        # tests del lab (pendiente)
```
