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

## Nuevas implementaciones (Manual QA AI v12)

**`AgentPolicy`** — enforcement de políticas y validación de tool calls (§18.6 + Cap 27):

```python
from src.agent_policy import AgentPolicy, enforce_policy, validate_tool_call, PolicyViolationError

policy = AgentPolicy(
    allowed_tools={"search", "calculate", "summarize"},
    sandbox_root="/tmp/sandbox",
    max_iterations=12,
    max_cost_usd=1.0,
    human_approval_required={"send_email", "execute_payment", "delete_record"},
)

# Valida antes de ejecutar cada tool call
try:
    enforce_policy("send_email", {"to": "user@example.com"}, policy,
                   iterations_so_far=3, cost_so_far=0.2, human_approved=False)
except PolicyViolationError as e:
    print(f"Bloqueado: {e}")  # requiere aprobación humana

# Valida schema JSON de argumentos
errors = validate_tool_call("search", {"query": "python docs"}, tool_schemas)
# errors = [] si todo correcto
```

Gates: `allowed_tools`, `max_iterations=12`, `max_cost_usd=1.0`, `max_tokens=50_000`, `human_approval_required`.

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
