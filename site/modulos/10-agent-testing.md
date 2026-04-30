---
title: "10 — agent-testing"
---

# 10 — agent-testing

Evaluar agentes LLM: selección de herramientas, trayectorias y evaluación segura de expresiones.

<div class="module-layout">
<div class="module-main">

## El problema

Un agente LLM no solo genera texto: selecciona herramientas, ejecuta acciones y produce resultados que dependen de una secuencia de decisiones. Si el agente elige la herramienta incorrecta, el resultado puede ser correcto por accidente o incorrecto de forma silenciosa. Testear solo el output final no detecta si el agente llegó ahí por el camino correcto. Un agente que acierta por el camino equivocado no es un agente fiable — es un agente que fallará en cuanto la situación cambie ligeramente.

## Cómo funciona

Cada llamada al agente produce un `AgentResult` con dos componentes: el output final y la trayectoria, que es la secuencia de pares `(tool, result)` que el agente ejecutó para llegar ahí. Los tests verifican ambos.

```text
query  →  agente  →  tool1  →  result1
                  →  tool2  →  result2
                  →  ...
                  →  output final

trajectory = [(tool1, result1), (tool2, result2), ...]
```

`SimpleAgent` usa un evaluador AST puro para expresiones matemáticas: parsea el árbol sintáctico de la expresión sin llamar a `eval()`. Sin acceso a builtins, sin posibilidad de inyectar código mediante la query.

`AgentPolicy` proporciona enforcement programático de límites: herramientas permitidas, coste máximo por llamada, número máximo de iteraciones y lista de acciones que requieren aprobación humana explícita.

## Código paso a paso

El primer paso es ejecutar el agente y obtener el resultado completo, incluyendo la trayectoria.

```python
from src.simple_agent import SimpleAgent

agent = SimpleAgent()
result = agent.run("Calcula 15 * 23 + 47")

print(result.final_output)  # "392"
print(result.trajectory)    # lista de AgentStep
```

El objeto `result` contiene toda la información necesaria para verificar no solo qué respondió el agente, sino cómo llegó hasta ahí. El output final correcto es condición necesaria pero no suficiente.

El segundo paso es verificar la trayectoria paso a paso. Cada `AgentStep` expone el nombre de la herramienta utilizada y el resultado que produjo.

```python
# Verificar que el agente tomó el camino correcto
assert result.trajectory[0].tool == "calculate"
assert result.trajectory[0].result == "392"
assert result.final_output == "392"

# Para queries más complejas, verificar la secuencia completa
result2 = agent.run("Busca el precio del producto X y calcula el IVA")
assert result2.trajectory[0].tool == "search"
assert result2.trajectory[1].tool == "calculate"
```

Cuando el agente gana herramientas, un prompt de sistema no es suficiente para controlar qué puede hacer. El tercer paso es añadir `AgentPolicy` con enforcement programático.

```python
from src.agent_policy import AgentPolicy, enforce_policy, PolicyViolationError

policy = AgentPolicy(
    allowed_tools={"search", "calculate", "summarize"},
    max_iterations=12,
    max_cost_usd=1.0,
    human_approval_required={"send_email", "execute_payment", "delete_record"},
)

try:
    enforce_policy(
        "send_email",
        {"to": "user@example.com"},
        policy,
        iterations_so_far=3,
        cost_so_far=0.20,
        human_approved=False,
    )
except PolicyViolationError as e:
    print(f"Bloqueado: {e}")  # requiere aprobación humana
```

`enforce_policy` lanza `PolicyViolationError` antes de ejecutar la acción, no después. Si el enforcement se hiciera post-ejecución, el daño ya estaría hecho.

## Técnicas avanzadas

A medida que el agente gana herramientas, un prompt de sistema ya no es suficiente para controlar qué puede hacer. `AgentPolicy` proporciona enforcement programático: si el agente intenta llamar una herramienta no autorizada o superar el coste máximo, lanza `PolicyViolationError` antes de ejecutar la acción.

`AgentGoalAccuracy` evalúa si el agente completó el objetivo del usuario, no solo si ejecutó los pasos. La diferencia importa: un agente puede ejecutar perfectamente todos los pasos y aun así no resolver el problema que el usuario tenía.

```python
from src.agent_metrics import (
    compute_recovery_rate,
    compute_human_handoff_rate,
    AgentMetricsReport,
)

# recovery_rate: fracción de fallos que se recuperaron con retry
recovery = compute_recovery_rate([(True, True), (True, False), (False, False)])
print(recovery.rate)  # 0.5 — 1 de 2 fallos recuperado

report = AgentMetricsReport(
    tool_accuracy=0.95,
    goal_achievement_rate=0.90,
    recovery_rate=0.80,
    human_handoff_rate=0.10,
    context_retention_rate=0.85,
    hallucination_rate_per_tool=0.05,
)
print(report.overall_health)  # media ponderada de todas las métricas
```

## Errores comunes

- ❌ Solo verificar el output final — el agente puede acertar por el camino equivocado, lo que significa que fallará en casos ligeramente diferentes. ✅ Siempre verificar la trayectoria completa, no solo el output.
- ❌ Usar `eval()` para expresiones del usuario — un usuario puede inyectar código arbitrario mediante la query matemática. ✅ Usar el evaluador AST-safe que parsea el árbol sintáctico sin ejecutar builtins.
- ❌ Sin límite de iteraciones — el agente puede entrar en bucles infinitos ante inputs inesperados. ✅ Configurar `max_iterations` en `AgentPolicy` y testear que se lanza `PolicyViolationError` al superarlo.
- ❌ Sin `human_approval_required` para acciones destructivas — el agente puede eliminar datos o enviar emails sin confirmación ante un prompt del usuario. ✅ Listar explícitamente en `AgentPolicy` todas las acciones que requieren aprobación, y testear que el enforcement funciona aunque el prompt lo pida directamente.

## En producción

| Métrica | Gate |
|---------|------|
| `tool_accuracy` | ≥ 0.90 |
| `goal_accuracy` | ≥ 0.85 |
| `max_cost_usd` por llamada | ≤ 1.00 |
| `max_iterations` | ≤ 12 |

```bash
pytest modules/10-agent-testing/tests/ -m "not slow" -q
```

Para seguridad del agente (excessive agency, prompt injection en agentes) consulta el módulo 08.

## Caso real

Una empresa de logística desplegó un agente de planificación de rutas con acceso a cinco herramientas: `buscar_ruta`, `calcular_coste`, `reservar_vehiculo`, `enviar_confirmacion` y `cancelar_reserva`. El agente superaba todos los tests de output final: las rutas que generaba eran correctas y los costes calculados eran precisos.

En los tests de trajectory evaluation, se detectó que el agente llamaba a `reservar_vehiculo` antes de `calcular_coste` en el 18% de los casos. El patrón ocurría cuando la query del usuario incluía urgencia ("lo antes posible", "para hoy"). El agente priorizaba la reserva sobre la validación de coste, generando reservas sin aprobación de presupuesto.

El test de trajectory evaluation detectó la anomalía antes de que llegara a producción. Se añadió `reservar_vehiculo` a `human_approval_required` hasta que se corrigiera el orden de la trayectoria. El fix en el prompt redujo el porcentaje de orden incorrecto a 0% en el conjunto de evaluación.

## Ejercicios

**🟢 Básico** — Ejecuta `SimpleAgent` con tres queries diferentes (una matemática, una de búsqueda, una ambigua) y verifica que `trajectory[0].tool` es el esperado en cada caso. El archivo de test es `modules/10-agent-testing/tests/test_agent_testing.py`:

```bash
pytest modules/10-agent-testing/tests/test_agent_testing.py -m "not slow" -q
```

¿Qué herramienta selecciona el agente cuando la query es ambigua? ¿Es consistente entre ejecuciones?

**🟡 Intermedio** — Añade una herramienta nueva al agente (`convert_currency`). Siguiendo TDD: escribe primero el test de trayectoria que verifica que el agente la usa cuando la query menciona conversión de moneda, luego implementa la herramienta. Verifica que los tests existentes siguen pasando.

**🔴 Avanzado** — Implementa una `AgentPolicy` con cuatro herramientas, de las cuales dos (`write_record`, `send_notification`) requieren aprobación humana. Diseña un test exhaustivo que verifique que el agente nunca ejecuta esas acciones aunque el prompt del usuario las pida explícitamente, y que `PolicyViolationError` contiene suficiente contexto para el log de auditoría.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">38</div>
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
