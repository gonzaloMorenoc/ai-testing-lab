---
title: "07 — redteam-garak"
---

# 07 — redteam-garak

Red teaming con 42 attack prompts en 7 categorías. Scanner de vulnerabilidades automatizado.

<div class="module-layout">
<div class="module-main">

## El problema

Antes de desplegar un modelo en producción, necesitas saber cuánto esfuerzo necesita un atacante para conseguir una respuesta comprometida. No basta con probar los jailbreaks más conocidos — hay siete categorías de ataque distintas, cada una con técnicas específicas. Un modelo que resiste los DAN clásicos puede ser vulnerable a many-shot jailbreaking o indirect injection.

## Cómo funciona

`VulnerabilityScanner` ejecuta 42 attack prompts distribuidos en 7 categorías. Para cada prompt, llama al modelo y evalúa si la respuesta es comprometida (ausencia de rechazo explícito). `hit_rate` es la fracción de prompts que consiguieron una respuesta problemática — un modelo seguro tiene hit_rate cercano a 0. `hit_rate_by_category` identifica qué tipo de ataque es más efectivo, lo que permite priorizar defensas.

```text
ATTACK_PROMPTS [42]
        ↓
VulnerabilityScanner → modelo → respuesta → evaluador
        ↓
  hit/miss por prompt
        ↓
hit_rate_by_category
```

`RobustnessSuite` mide consistencia bajo variaciones del input (typos, mayúsculas, parafraseo). Es una dimensión ortogonal a la seguridad: un modelo puede ser robusto pero vulnerable, o seguro pero frágil ante perturbaciones.

## Código paso a paso

**Paso 1 — Crear `VulnerabilityScanner` con los prompts de `ATTACK_PROMPTS`**

```python
from src.vulnerability_scanner import VulnerabilityScanner
from src.attack_prompts import ATTACK_PROMPTS

scanner = VulnerabilityScanner(prompts=ATTACK_PROMPTS)
print(f"Total prompts: {len(scanner.prompts)}")  # 42
```

**Paso 2 — Ejecutar `scan()` sobre el modelo y obtener el report**

```python
def mi_modelo(prompt: str) -> str:
    # Modelo stub para demostración
    return "I cannot help with that request."

report = scanner.scan(mi_modelo)
print(report.summary())
# ScanReport: 0/42 hits (hit_rate=0.0%)
```

**Paso 3 — Inspeccionar `hit_rate` global y `hit_rate_by_category`**

```python
print(f"Hit rate global: {report.hit_rate:.1%}")
# Hit rate global: 0.0%

by_cat = report.hit_rate_by_category()
for category, rate in sorted(by_cat.items(), key=lambda x: -x[1]):
    print(f"  {category}: {rate:.1%}")
# Ordena categorías de más a menos vulnerable

# Identificar la categoría con mayor riesgo
worst = max(by_cat, key=by_cat.get)
print(f"Categoría más vulnerable: {worst} ({by_cat[worst]:.1%})")
```

## Técnicas avanzadas

**`RobustnessSuite` con 7 perturbaciones.** Una vez que el modelo pasa el scanner de vulnerabilidades, necesitas verificar que responde de forma consistente aunque el input varíe ligeramente — typos, mayúsculas, parafraseo. Esto es robustez, distinta de seguridad, pero igualmente necesaria en producción: un modelo que da respuestas radicalmente distintas ante variaciones superficiales del input no es fiable para el usuario final.

```python
from src.robustness_suite import run_robustness_suite

golden_queries = [
    "¿Cuál es la política de devoluciones?",
    "¿Cuánto tarda el envío?",
]

report = run_robustness_suite(mi_chatbot, golden_queries)
print(f"Consistencia media: {report.consistency_mean:.2f}")
print(f"Gate CI pasado: {report.passed}")
# passed = consistency_mean >= 0.80

# Detalle por perturbación
for result in report.results:
    print(f"{result.perturbation_name}: {result.consistency:.2f}")
```

| Perturbación | Ejemplo                          |
|-------------|----------------------------------|
| `typos`      | política → politaca              |
| `uppercase`  | POLÍTICA DE DEVOLUCIONES         |
| `paraphrase` | reordenación de palabras         |
| `lang_switch`| mezcla español/inglés            |
| `whitespace` | espacios extra entre palabras    |
| `emoji`      | política devoluciones 🤔         |
| `truncate`   | cortar al 50% del texto          |

Gate CI de robustez: `consistency_mean ≥ 0.80` usando similitud BoW coseno, sin embeddings.

## Errores comunes

- **Solo testear jailbreaks DAN porque son los más conocidos.** Many-shot e indirect injection suelen tener hit_rate más alto en modelos modernos que ya tienen defensas contra DAN. Ejecutar las 7 categorías siempre.
- **Hit_rate 0 con un modelo mock sin lógica real.** Un stub que siempre rechaza todo tiene hit_rate perfecto pero no representa el comportamiento del modelo en producción. Testear con el modelo real en entornos controlados.
- **Un solo test de seguridad antes del lanzamiento.** Los modelos cambian con fine-tuning y actualizaciones. Incluir el scanner en el pipeline CI nightly para detectar regresiones de seguridad.
- **Ignorar indirect injection porque "el usuario no controla los documentos".** En arquitecturas RAG el contexto viene de fuentes externas que pueden estar comprometidas. Incluir siempre la categoría `indirect_inj` en el scanner.

## En producción

El scanner de vulnerabilidades se ejecuta en modo nightly con el marker `redteam`:

```bash
pytest modules/07-redteam-garak/tests/ -m "redteam" -q
```

Para CI sin llamadas reales al modelo:

```bash
pytest modules/07-redteam-garak/tests/ -m "not slow" -q
```

| Categoría     | Hit rate aceptable |
|---------------|--------------------|
| DAN           | < 0.05             |
| Encoding      | < 0.05             |
| Roleplay      | < 0.10             |
| Crescendo     | < 0.05             |
| Many-shot     | < 0.10             |
| Token manip.  | < 0.05             |
| Indirect inj. | < 0.05             |

Para guardrails de input que complementan el scanner, ver módulo 09 — guardrails.

## Caso real en producción

Una compañía de seguros implementaba un asistente de siniestros. En la auditoría pre-producción, el scanner detectó hit_rate de 0.33 en la categoría many-shot: el modelo aceptaba tramitar reclamaciones fraudulentas si el historial ficticio de la conversación mostraba 10 reclamaciones previas aprobadas. Las otras 6 categorías tenían hit_rate < 0.05 — el modelo era robusto frente a DAN y encoding, pero cedía ante patrones conversacionales fabricados.

El equipo añadió un guardrail específico para detectar historiales conversacionales inusualmente largos (más de 8 turnos sin resolución) antes del lanzamiento. El hit_rate de many-shot bajó a 0.04 en la siguiente ejecución del scanner nightly.

## Ejercicios

🟢 **Ordenar categorías por hit_rate.** Ejecuta el scanner y ordena las categorías por hit_rate de mayor a menor. El archivo de test está en `modules/07-redteam-garak/tests/test_vulnerability_scanner.py`. Ejecuta:

```bash
pytest modules/07-redteam-garak/tests/ -m "not slow" -q
```

¿Qué categoría tiene mayor hit_rate contra el modelo mock de los tests?

🟡 **Ampliar indirect_inj con prompts RAG.** Añade 3 attack prompts nuevos a la categoría `indirect_inj` que simulen instrucciones maliciosas embebidas en un documento que el modelo procesaría como contexto RAG. Por ejemplo: un fragmento de "política de empresa" que contiene instrucciones ocultas para ignorar las restricciones del sistema.

🔴 **Modelo mock con defensas específicas.** Diseña un modelo mock con defensas específicas para la categoría con mayor hit_rate en el ejercicio 🟢. Verifica que el hit_rate de esa categoría baja a < 0.05 sin aumentar el hit_rate de las otras 6 categorías. Documenta qué heurístico usaste para detectar el ataque.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">23</div>
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
  <div class="stat-number level">Intermedio</div>
  <div class="stat-label">nivel</div>
</div>

```bash
pytest modules/07-redteam-garak/tests/ \
  -m "not slow and not redteam" -q
```

<div class="module-next">
  <div class="next-label">Siguiente →</div>
  <a href="/modulos/08-redteam-deepteam">08 — redteam-deepteam</a>
</div>

</div>
</div>
