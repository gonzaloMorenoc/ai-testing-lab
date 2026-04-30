---
title: "09 — guardrails"
---

# 09 — guardrails

Validación de entrada y salida con Guardrails AI y NeMo Guardrails.

<div class="module-layout">
<div class="module-main">

## El problema

Tu LLM puede filtrar información personal que los usuarios introducen en sus queries. O puede generar respuestas que incluyen datos sensibles extraídos del contexto RAG. Ninguno de los dos casos es aceptable bajo GDPR. Un pipeline sin guardrails de entrada y salida no es solo un riesgo técnico: es un riesgo legal. Los guardrails son la última línea de defensa antes de que el contenido llegue al usuario, y necesitan cubrir ambos extremos del flujo.

## Cómo funciona

La validación ocurre en dos puntos del pipeline: antes de llamar al LLM (input) y antes de devolver la respuesta (output). Saltarse cualquiera de los dos deja una ventana abierta.

```text
user_input  →  PII_check  →  [bloqueado / limpio]  →  LLM
                                                         ↓
usuario  ←  [bloqueado / limpio]  ←  PII_check  ←  output
```

La detección de PII usa seis patrones regex (teléfonos ES, emails, DNI/NIE, IBANs, tarjetas de crédito, números de seguridad social). Es determinista y no requiere LLM, lo que garantiza latencia constante y reproducibilidad.

Los canary tokens funcionan de manera diferente: se inyecta un identificador único en el system prompt. Si ese token aparece en cualquier respuesta del modelo, el modelo está filtrando su propio system prompt, que puede contener instrucciones de negocio confidenciales o claves de configuración.

`PIILeakageError` usa `raise`, no `assert`. Los asserts se desactivan completamente con `python -O`; una verificación de seguridad que puede ignorarse no es una verificación.

## Código paso a paso

Empieza con el flujo más básico: un input que contiene PII y la respuesta del pipeline.

```python
from src.input_validator import InputValidator

validator = InputValidator()
result = validator.validate("Mi email es usuario@ejemplo.com. ¿Cuál es mi saldo?")

print(result.valid)      # False — PII detectada en el input
print(result.reason)     # "PII detected: email"
print(result.matches)    # {"email": ["usuario@ejemplo.com"]}
```

El resultado incluye exactamente qué elementos de PII se detectaron. Registra esa información en tus logs de auditoría antes de descartar la request; es el rastro que necesitas si tienes que demostrar cumplimiento.

El segundo punto de validación es el output. El modelo puede recibir un input limpio pero generar una respuesta que incluye PII extraída de documentos en el contexto RAG. Valida el output independientemente del input.

```python
from src.pii_canary import detect_pii_in_response, check_no_pii_in_response, PIILeakageError

response = mi_modelo("¿Qué información tenemos sobre este cliente?")

matches = detect_pii_in_response(response)
# [PIIMatch(entity_type="phone_es", ...), PIIMatch(entity_type="email", ...)]

try:
    check_no_pii_in_response(response)
except PIILeakageError as e:
    print(f"PII detectada en output: {e}")
    # bloquear antes de devolver al usuario
```

El tercer mecanismo protege tu propio system prompt. Genera un canary único por entorno o sesión y verifica que nunca aparece en las respuestas.

```python
from src.pii_canary import generate_canary, test_no_system_prompt_leak

canary = generate_canary()  # e.g. "CANARY-A3F2B891CD012345"

result = test_no_system_prompt_leak(mi_chatbot, canary)
print(result.passed)          # True si el system prompt no se filtra
print(result.leaks_detected)  # 0 si ningún probe reveló el canary
print(result.leaked_in)       # () — tupla de probes donde hubo fuga
```

## Técnicas avanzadas

Los guardrails de input y output protegen los datos del usuario. Pero también necesitas verificar que el modelo no filtra tu propio system prompt — que puede contener instrucciones de negocio confidenciales o claves de configuración.

Los patrones de PII incluyen formatos españoles específicos que los sistemas genéricos suelen omitir:

| Tipo | Patrón cubre |
|------|-------------|
| `email` | Formato estándar RFC 5322 |
| `phone_es` | Móviles `6xx`/`7xx`, fijos `9xx`, con/sin `+34` |
| `dni_es` | 8 dígitos + letra verificadora |
| `iban_es` | `ES` + 22 dígitos |
| `credit_card` | Luhn, 13-16 dígitos, con/sin espacios |
| `ssn` | Número de seguridad social US (patrón adicional) |

Usa `detect_pii_in_response` con los seis patrones habilitados incluso en tests de regresión — un cambio en el prompt template puede hacer que el modelo empiece a incluir datos que antes no incluía.

## Errores comunes

- ❌ Validar solo el input — el output puede contener PII extraída del contexto RAG, de otros documentos o del historial de conversación. ✅ Validar siempre input Y output como dos pasos independientes.
- ❌ Usar `assert` para errores de seguridad — `python -O` desactiva todos los asserts silenciosamente en producción. ✅ Usar `raise PIILeakageError` con un mensaje descriptivo.
- ❌ No testear fugas del system prompt — el modelo puede revelar instrucciones confidenciales ante preguntas directas o prompts crafteados. ✅ Usar `generate_canary` en cada entorno y ejecutar `test_no_system_prompt_leak` en el pipeline de CI.
- ❌ Guardrails solo con patrones de inglés — los datos personales en español tienen formatos distintos (DNI con letra, IBAN con prefijo ES, teléfonos con `+34`). ✅ Incluir los seis patrones ES del módulo.

## En producción

| Guardrail | Acción si activa |
|-----------|-----------------|
| PII en input | Bloquear + registrar en log de auditoría |
| PII en output | Bloquear + registrar en log de auditoría |
| Canary en output | Alerta inmediata + auditoría completa de sesión |
| Prompt injection | Bloquear + alerta de seguridad |

```bash
pytest modules/09-guardrails/tests/ -m "not slow" -q
```

Para detectar ataques de indirect injection que pueden bypassar estos guardrails, consulta el módulo 07.

## Caso real

Una consultora de RRHH desplegó un chatbot que procesaba CVs y respondía preguntas de candidatos. El pipeline tenía validación de input, pero no de output. El modelo tenía acceso a un contexto RAG con información de todos los candidatos para poder responder preguntas contextuales.

En una auditoría interna, `detect_pii_in_response` identificó 23 casos en 500 interacciones auditadas donde el modelo incluía el email de otros candidatos en sus respuestas. El patrón era consistente: cuando un candidato preguntaba sobre el proceso de selección en términos similares a la query de otro candidato, el modelo recuperaba el documento de ese otro candidato y a veces incluía su email como referencia.

Se añadió la validación de output con el patrón de email como gate obligatorio antes del despliegue a producción. También se revisó la estrategia de retrieval para evitar que documentos de un candidato fueran accesibles en el contexto de otro.

## Ejercicios

**🟢 Básico** — Construye un input que contenga un DNI español (`12345678Z`) y un email. El archivo de test es `modules/09-guardrails/tests/test_guardrails.py`:

```bash
pytest modules/09-guardrails/tests/test_guardrails.py -m "not slow" -q
```

¿`InputValidator` bloquea el input? ¿`matches` lista ambos elementos? Prueba con un DNI con letra minúscula y observa si el patrón sigue detectándolo.

**🟡 Intermedio** — Implementa un test que verifique que un modelo stub que repite literalmente el system prompt es detectado por `test_no_system_prompt_leak`. ¿Qué umbral de similitud usarías para evitar falsos positivos cuando el modelo menciona partes del system prompt de forma paráfraseada?

**🔴 Avanzado** — Diseña un pipeline de doble guardrail (input + output) que procese 20 queries, bloquee las que contienen PII en cualquiera de los dos extremos, registre las incidencias con timestamp y tipo de PII detectado, y genere un informe de auditoría con conteos por tipo. El informe debe poder exportarse como JSON para integrarse con un sistema de compliance.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">11</div>
  <div class="stat-label">tests</div>
</div>

<div class="stat-card">
  <div class="stat-number">0.06s</div>
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
pytest modules/09-guardrails/tests/ \
  -m "not slow" -q
```

<div class="module-next">
  <div class="next-label">Siguiente →</div>
  <a href="/modulos/10-agent-testing">10 — agent-testing</a>
</div>

</div>
</div>
