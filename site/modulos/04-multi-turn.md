# 04 — multi-turn

**Concepto:** Testear conversaciones de múltiples turnos y retención de información.

**Tests:** 10 · **Tiempo:** ~0.05s · **API key:** no necesaria

## Qué aprenderás

- `ConversationalTestCase` y cómo estructurar tests de diálogo
- Por qué el tamaño de la ventana de contexto importa (configurado en 8 turnos)
- Cómo verificar que la información del turno 1 sigue disponible en el turno 9
- Detección de contradicciones entre turnos

## Ejecutar

```bash
pytest modules/04-multi-turn/tests/ -m "not slow" -q
```

## Código de ejemplo

```python
from src.multi_turn_rag import MultiTurnRAG

rag = MultiTurnRAG()
rag.respond("¿Cuál es la política de devoluciones?")  # turno 1

# 7 turnos sobre otro tema...
for _ in range(7):
    rag.respond("¿Cuánto tarda el envío?")

# El turno 9 debe recordar el turno 1
response = rag.respond("¿Qué me dijiste sobre las devoluciones?")
assert "30 días" in response or "devolución" in response.lower()
```

## Por qué importa

Un sistema RAG con ventana de contexto pequeña "olvida" información relevante a medida que avanza la conversación. El usuario siente que el sistema no le presta atención.
