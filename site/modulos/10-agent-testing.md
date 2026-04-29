# 10 — agent-testing

**Concepto:** Evaluar agentes LLM: selección de herramientas, trayectorias y evaluación segura de expresiones.

**Tests:** 9 · **Tiempo:** ~0.05s · **API key:** no necesaria

## Qué aprenderás

- Tool accuracy: ¿el agente selecciona la herramienta correcta para cada query?
- Trajectory evaluation: ¿el agente llega al resultado correcto por el camino correcto?
- AST-safe eval: cómo evaluar expresiones matemáticas sin `eval()` inseguro
- `AgentGoalAccuracy`: ¿el agente completó el objetivo del usuario?

## Ejecutar

```bash
pytest modules/10-agent-testing/tests/ -m "not slow" -q
```

## Código de ejemplo

```python
from src.simple_agent import SimpleAgent

agent = SimpleAgent()
result = agent.run("Calcula 15 * 23 + 47")

# Verificar la trayectoria
assert result.trajectory[0].tool == "calculate"
assert result.trajectory[0].result == "392"
assert result.final_output == "392"
```

El `calculate` interno usa un evaluador AST puro — sin `eval()`, sin acceso a builtins, sin riesgo de inyección de código.

## Por qué importa

Los tests de agentes deben verificar no solo el resultado final sino también el proceso. Un agente que llega al resultado correcto por el camino equivocado (herramienta incorrecta, pasos innecesarios) no es un agente fiable.
