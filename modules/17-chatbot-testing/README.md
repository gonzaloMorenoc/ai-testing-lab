# 17 — chatbot-testing

Capítulo 10 del Manual QA AI v13: **testing de chatbots productivos**, las 8 áreas operativas que una batería RAGAS por sí sola NO cubre.

## Quickstart

```bash
pytest modules/17-chatbot-testing/tests/ -q
```

```
60 passed in 0.08s
```

## Las 8 áreas (Tabla 10.2)

| # | Área | Métrica | Umbral objetivo | Mínimo casos |
|---|---|---|---:|---:|
| 1 | Intent detection | `intent_accuracy` | ≥ 0.90 | 20 |
| 2 | Fallback (fuera de dominio) | `correct_fallback_rate` | ≥ 0.90 | 20 |
| 3 | Escalado humano | `escalation_precision` | ≥ 0.95 | 20 |
| 4 | Tono y persona | `tone_score` | ≥ 0.80 | 20 |
| 5 | Memoria | `context_retention` | ≥ 0.85 | 20 |
| 6 | Aislamiento de sesiones | `session_isolation` | **= 1.00** | 10 |
| 7 | Conversación larga | `long_context_consistency` | ≥ 0.80 (N=20) | 10 |
| 8 | Recuperación de errores | `recovery_success_rate` | ≥ 0.90 | 20 |

## API pública

| Módulo | Símbolos clave |
|---|---|
| `chatbot_areas` | `ChatbotTestArea`, `AREA_SPECS` (Tabla 10.2) |
| `intent_classifier` | `predict_intent`, `evaluate_intent_accuracy` |
| `session_manager` | `Session`, `SessionManager`, `verify_isolation` |
| `tone_evaluator` | `evaluate_tone`, `tone_consistency` |
| `escalation_policy` | `should_escalate`, `evaluate_escalation_precision` |
| `error_recovery` | `classify_error`, `decide_recovery`, `recovery_success_rate` |

## Por qué un módulo dedicado

RAGAS y DeepEval cubren las dimensiones **semánticas** del bot (faithfulness, relevancy, correctness), pero **no** cubren las operativas:
- Si el bot escala a humano cuando no debe, RAGAS sigue marcando faithfulness=0.95.
- Si dos sesiones concurrentes filtran datos entre sí, RAGAS no se entera.
- Si el tono se desliza a informal en turno 8, RAGAS no lo distingue de la respuesta canónica.

Las 8 áreas son la batería mínima operativa que cualquier chatbot productivo necesita además de las métricas semánticas.

## Testing manual vs automatizado

El manual §10.4 documenta que el testing manual sigue siendo necesario en:
- **Ambigüedad cultural**: el bot suena "raro" sin que las métricas lo capten.
- **Tono y adecuación de marca**: una respuesta correcta puede sonar fría o pedante.
- **Métricas de satisfacción reales**: CSAT post-conversación, thumbs up/down, tasa de abandono medio de sesión.

El testing automatizado del módulo cubre las 8 áreas con métricas objetivas y deterministas. El testing manual lo complementa para los aspectos que no pueden automatizarse de forma fiable.

## Estructura

```
modules/17-chatbot-testing/
├── conftest.py
├── src/
│   ├── chatbot_areas.py        # Tabla 10.2 codificada
│   ├── intent_classifier.py    # Mock NLU + métricas
│   ├── session_manager.py      # Sesiones + verify_isolation
│   ├── tone_evaluator.py       # Evaluación de tono (mock heurístico)
│   ├── escalation_policy.py    # Política de escalado humano
│   └── error_recovery.py       # Recovery con backoff exponencial
└── tests/                      # 60 tests
```

## Diferencias con otros módulos del repo

- **04-multi-turn** cubre métricas multi-turno (`context_retention`, `coreference_resolution`); el módulo 17 las usa pero añade tests operativos del wrapper.
- **08-redteam-deepteam** cubre safety/refusal; el módulo 17 cubre el complementario: false refusal, escalado correcto.
- **09-guardrails** cubre validación input/output; el módulo 17 cubre el "happy path" operacional del chatbot.

## Referencias

- Manual QA AI v13 — Cap. 10 (pp. 40–41), Tabla 10.1 (tipos de tests), Tabla 10.2 (matriz operativa)
- Cap. 16 — Evaluación multi-turno (complementa este módulo en el área 5 y 7)
