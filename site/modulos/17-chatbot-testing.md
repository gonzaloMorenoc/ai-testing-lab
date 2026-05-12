---
title: "17 — chatbot-testing"
---

# 17 — chatbot-testing

Las 8 áreas operativas de testing que una batería RAGAS NO cubre. Si tu chatbot pasa las métricas semánticas pero falla en producción, este módulo te dice exactamente dónde mirar.

## El problema

Tu suite RAGAS reporta `faithfulness=0.92` y `answer_relevancy=0.91`. El chatbot va a producción y a las dos semanas:

- El equipo de soporte recibe quejas porque el bot escala a humano demasiadas veces (false refusal).
- Un cliente reporta que el bot lo trató con "tú" cuando la marca es formal (deriva de tono).
- Otro cliente ve fragmentos del prompt de su empresa anterior (sesiones contaminadas).
- En conversaciones de 15+ turnos el bot se contradice.

Ninguna de las métricas RAGAS habría detectado nada de esto. El **Capítulo 10 del manual v13** define las 8 áreas operativas que toda batería de chatbot productivo debe cubrir.

## Las 8 áreas

| # | Área | Métrica | Objetivo | Por qué |
|---|---|---|:---:|---|
| 1 | **Intent detection** | `intent_accuracy` | ≥ 0.90 | Si el clasificador falla, todo lo demás está perdido |
| 2 | **Fallback** | `correct_fallback_rate` | ≥ 0.90 | Queries fuera de dominio sin alucinaciones |
| 3 | **Escalado humano** | `escalation_precision` | ≥ 0.95 | El coste de NO escalar un caso crítico es alto |
| 4 | **Tono y persona** | `tone_score` | ≥ 0.80 | La marca tiene una voz; el bot debe respetarla |
| 5 | **Memoria** | `context_retention` | ≥ 0.85 | Recordar lo dicho en turnos anteriores |
| 6 | **Aislamiento de sesiones** | `session_isolation` | **= 1.00** | No negociable: 0 fugas entre usuarios |
| 7 | **Conversación larga** | `long_context_consistency` | ≥ 0.80 a N=20 | Degradación tras N turnos |
| 8 | **Recuperación de errores** | `recovery_success_rate` | ≥ 0.90 | Manejo de tool/API/timeout fallido |

## Cómo se usa

```python
# Área 1 — Intent detection
from intent_classifier import predict_intent, evaluate_intent_accuracy

result = evaluate_intent_accuracy([
    ("quiero devolver un pedido", "policy_returns"),
    ("dame mi factura de marzo", "billing"),
    ("hablar con humano", "human_support"),
])
assert result["accuracy"] >= 0.90

# Área 3 — Escalado humano
from escalation_policy import should_escalate

decision = should_escalate("quiero poner una denuncia")
assert decision.should_escalate
assert decision.reason == "critical_keyword_detected"

# Área 6 — Aislamiento de sesiones
from session_manager import SessionManager, verify_isolation

mgr = SessionManager()
s1 = mgr.new_session("user-A")
s2 = mgr.new_session("user-B")
s1.remember("password", "secret-A")
s2.remember("password", "secret-B")

assert verify_isolation(mgr), "Las sesiones comparten contexto: fuga grave"
assert s1.recall("password") == "secret-A"
assert s2.recall("password") == "secret-B"

# Área 8 — Recuperación con backoff exponencial
from error_recovery import ErrorKind, decide_recovery

decision = decide_recovery(ErrorKind.TRANSIENT, retry_count=1)
assert decision.retry
assert decision.backoff_seconds == 2.0  # 2^1
```

## Testing manual vs automatizado (§10.4)

El testing automatizado del módulo cubre las dimensiones objetivas. El **testing manual estructurado** sigue siendo necesario en tres áreas:

- **Ambigüedad cultural**: una respuesta puede ser correcta pero sonar "rara" en el mercado objetivo. Requiere revisión por hablantes nativos.
- **Tono profesional sutil**: el bot puede pasar el `tone_score` y aun así sonar pedante o frío. Requiere panel humano.
- **Métricas de satisfacción reales**: CSAT post-conversación, thumbs up/down, tasa de abandono medio de sesión.

El manual recomienda asignar **20 casos por área** revisados por experto en cada release.

## Diferencia con red teaming y robustness

- El módulo 17 cubre el **happy path operacional** del chatbot.
- Módulo 07/08 (red-team) cubre payloads maliciosos.
- Módulo 18 (robustness) cubre perturbaciones del input legítimo.

Tres baterías distintas, ningún solapamiento.

## Integración con la Tabla 4.2

Los umbrales del manual están centralizados en [`qa_thresholds.py`](https://github.com/gonzaloMorenoc/ai-testing-lab/blob/main/qa_thresholds.py). El módulo importa los umbrales de las métricas comunes (`refusal_rate`, `false_refusal_rate`) y mantiene los específicos de chatbot en `AREA_SPECS`.

## Referencias

- Manual QA AI v13 — Cap. 10 (pp. 40–41), Tabla 10.1, Tabla 10.2
- Cap. 16 — Evaluación multi-turno (complementa áreas 5 y 7)
- [Módulo 04 — multi-turn](./04-multi-turn): métricas multi-turno detalladas
