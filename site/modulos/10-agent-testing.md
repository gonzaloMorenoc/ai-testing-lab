---
title: "10 — agent-testing"
---

# 10 — agent-testing

Evaluar agentes LLM: selección de herramientas, trayectorias y evaluación segura de expresiones.

<div class="module-layout">
<div class="module-main">

## Qué aprenderás

- Tool accuracy: ¿el agente selecciona la herramienta correcta para cada query?
- Trajectory evaluation: ¿el agente llega al resultado correcto por el camino correcto?
- AST-safe eval: cómo evaluar expresiones matemáticas sin `eval()` inseguro
- `AgentGoalAccuracy`: ¿el agente completó el objetivo del usuario?

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

> Los tests de agentes deben verificar no solo el resultado final sino también el proceso. Un agente que llega al resultado correcto por el camino equivocado no es un agente fiable.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">10</div>
  <div class="stat-label">tests</div>
</div>

<div class="stat-card">
  <div class="stat-number">0.05s</div>
  <div class="stat-label">duración</div>
</div>

<div class="stat-card stat-ok">
  <div class="stat-number">✓</div>
  <div class="stat-label">sin API key</div>
</div>

<div class="stat-card">
  <div class="stat-number level">Avanzado</div>
  <div class="stat-label">nivel</div>
</div>

```bash
pytest modules/10-agent-testing/tests/ \
  -m "not slow" -q
```

<div class="module-next">
  <div class="next-label">Siguiente →</div>
  <a href="/modulos/11-playwright-streaming">11 — playwright-streaming</a>
</div>

</div>
</div>
