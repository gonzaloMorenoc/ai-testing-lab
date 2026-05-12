---
title: "Reproducibilidad y determinismo en QA AI"
description: "Por qué los tests de LLMs nunca son deterministas al 100 %, cuáles son las 4 fuentes de no-determinismo, y el patrón canónico para hacer tests aproximadamente reproducibles."
---

# Reproducibilidad y determinismo

Los tests deterministas son la base del QA clásico: misma entrada, misma salida, una y otra vez. En sistemas LLM esa garantía se rompe en al menos cuatro niveles. Sin un tratamiento explícito, los tests se vuelven flaky y los gates pierden su capacidad de bloquear.

Este capítulo es transversal: consolida pistas dispersas a lo largo del manual (semillas, `rng_seed`, `temperature=0`) en una guía operativa única.

## El mito de `temperature=0`

`temperature=0` reduce la varianza, pero **no garantiza determinismo bit a bit** en proveedores reales. Tres motivos:

1. **Empates en logits.** Cuando dos tokens tienen logits idénticos en float, el orden de muestreo depende del kernel GPU usado.
2. **Ejecución batched no determinista.** Los kernels async de GPU pueden producir resultados ligeramente distintos según la carga de la batch.
3. **Routing entre snapshots.** OpenAI y Anthropic pueden enrutar tu request a distintos snapshots del modelo (mismo nombre, distinto build).

::: warning Antipatrón frecuente
Diseñar tests con `assert response == expected_response` y temperatura cero es un antipatrón. Aunque pase hoy, va a fallar cualquier semana sin que cambies código.
:::

## Las 4 fuentes de no-determinismo

| Nivel | Fuente | Mitigación realista |
|---|---|---|
| Modelo | Sampling estocástico (`temperature`, `top_p`, `top_k`) | `temperature=0` + `top_p=1`; documentar que no garantiza determinismo |
| Proveedor | Rate limits, fallback de routing, load balancing entre regiones | Pinning explícito al snapshot exacto (`claude-sonnet-4-5`, no `claude-sonnet-latest`); cabecera de versión visible en logs |
| Tokenizer | Cambios entre versiones afectan truncamiento y conteo | Fijar versión del cliente; cuenta de tokens verificada en CI |
| Modelo cerrado | Actualizaciones silenciosas (Anthropic/OpenAI publican snapshots, no garantizan estabilidad bit a bit) | `system_fingerprint` cuando exista; smoke tests diarios con outputs canónicos |
| Embeddings | Modelos de embedding cerrados pueden cambiar sin aviso | Embeddings open-source (BAAI/bge, sentence-transformers) con versión fijada para evaluación |
| Pipeline RAG | Tie-breaking en retrieval cuando hay scores empatados | Orden estable por `(score, doc_id)`; registrar el orden recuperado en el trace |
| Evaluador | LLM-as-Judge tiene su propia varianza | Mediana sobre N evaluaciones por ejemplo (N=3 ó 5); reportar IC95 |

## El patrón canónico: tests aproximadamente reproducibles

En lugar de un test pass/fail por ejecución, ejecutar N veces y evaluar la distribución. **El gate pasa si la cota inferior del IC95 supera el umbral.** Esto convierte un test estocástico en una decisión estadísticamente sólida:

```python
import numpy as np

N_RUNS = 5  # 3-5 en PR, 10-20 en release nightly

# ACCEPTANCE_MARGIN no es margen de error de medida (eso lo aporta el IC95).
# Es un margen de aceptación intencional sobre el umbral nominal:
# con expected_threshold=0.85 y ACCEPTANCE_MARGIN=0.02, el sistema pasa
# cuando ci_low >= 0.83. Es decir, se acepta una banda de 2 puntos por
# debajo del objetivo siempre que la mediana siga por encima. Si se
# pone a 0, el gate exige IC95 entero por encima del umbral (más
# estricto). En alto riesgo, fijar a 0.
ACCEPTANCE_MARGIN = 0.02


def evaluate_with_variance(query: str, expected_threshold: float) -> dict:
    """Ejecuta el sistema N veces y reporta la distribución."""
    scores = [evaluate_once(query) for _ in range(N_RUNS)]
    median = float(np.median(scores))
    ci_low, ci_high = np.percentile(scores, [2.5, 97.5])
    return {
        "median": median,
        "ci95_low": float(ci_low),
        "ci95_high": float(ci_high),
        "iqr": float(np.percentile(scores, 75) - np.percentile(scores, 25)),
        "pass": median >= expected_threshold and (
            ci_low >= expected_threshold - ACCEPTANCE_MARGIN
        ),
    }


# Uso en un gate de PR (assert es válido en pytest):
result = evaluate_with_variance(query, expected_threshold=0.85)
assert result["pass"], (
    f"Faithfulness inestable o por debajo del umbral: "
    f"mediana={result['median']:.3f}, IC95=[{result['ci95_low']:.3f}, {result['ci95_high']:.3f}]"
)
```

Esto está implementado en [`05-prompt-regression/src/variance_evaluator.py`](https://github.com/gonzaloMorenoc/ai-testing-lab/blob/main/modules/05-prompt-regression/src/variance_evaluator.py).

## Reproducibilidad vs detección de drift: dos suites distintas

Hay tensión entre dos objetivos:
- "Mi test debe pasar siempre con la misma versión del modelo" (reproducibilidad).
- "Si el proveedor cambia el modelo, debo enterarme" (detección de drift).

La forma canónica de reconciliarlos es **separar dos suites complementarias**:

| Suite | Objetivo | Cuándo se ejecuta | Acción si falla |
|---|---|---|---|
| `pr_regression` | Reproducibilidad: cambios en código no rompen calidad | En cada PR (≤ 10 min) | Bloquear merge |
| `provider_drift` | Detección: el modelo del proveedor cambió bajo nosotros | Nightly o por tracking de fingerprint | Alertar a QA + congelar pinning más estricto |
| `reproducibility_audit` | Validación: el sistema completo se reconstruye desde código | Por release y trimestralmente | Bloquear release; abrir tarea de remediación |

## Seeds y `system_fingerprint`: lo que sí ayuda

- **`seed` (cuando el proveedor lo expone).** OpenAI lo permite vía parámetro; junto con `system_fingerprint` en la respuesta, indica mismo modelo + mismo seed = misma respuesta con muy alta probabilidad (no garantizado bit a bit).
- **`system_fingerprint` en el trace.** Registrar siempre. Un cambio inesperado de fingerprint con el mismo nombre del modelo es la señal canónica de que el proveedor lanzó un snapshot nuevo.
- **Pinning de versión exacta.** Nunca usar alias móviles (`*-latest`, `*-newest`). Pinned siempre al snapshot.
- **Cliente y dependencias congelados.** `requirements.txt` con `==` (no rangos). Reproducir el container de CI para auditorías.
- **Embeddings open para evaluación.** Re-indexar el corpus de evaluación con un embedder open-source de versión fijada. Modelos cerrados de embedding pueden cambiar entre runs.
- **RNG de Python/NumPy.** `np.random.default_rng(seed=42)` en bootstrap, paráfrasis y shuffling del eval set.

## Antipatrones de reproducibilidad

::: warning Los seis antipatrones a evitar
- **Asumir que `temperature=0` es determinista** y diseñar el test sobre igualdad exacta de strings.
- **Modelo móvil en producción y test.** `claude-3-haiku` se actualiza en ventana silenciosa; los tests verdes de ayer fallan hoy sin un solo commit. Pinning siempre.
- **Ignorar el embedder de evaluación.** El evaluador semántico usa `text-embedding-ada-002` con versión móvil. La métrica cambia sin que cambie el código del proyecto.
- **Único run por ejemplo en PR.** Con LLMs estocásticos, una ejecución no es una medida; es una muestra de tamaño 1. Mediana sobre N como mínimo en PRs de regresión de prompts.
- **Bisección imposible en agentes.** Golden traces no almacenados impiden reproducir la cadena exacta de tool calls que produjo un fallo. Trace schema obligatorio (Cap. 19).
- **Confundir flaky con bug.** Rerun-on-failure enmascara una caída de calidad real. La tasa de flakiness debe monitorizarse por separado y no debe superar el 2 % por suite.
:::

## Checklist operativo

Antes de declarar L3 o superior en el [modelo de madurez](./madurez), verificar:

- [ ] **Pinning de modelo** (snapshot exacto, nunca `*-latest`).
- [ ] **`system_fingerprint`** registrado en cada trace.
- [ ] **Embedder de evaluación open-source con versión fijada.**
- [ ] **`requirements.txt`** con `==` y reconstrucción del container de CI auditada.
- [ ] **Tests de PR usan mediana sobre N=3 ó 5**, no run único.
- [ ] **`rng_seed`** fijado en bootstrap, paráfrasis y shuffling.
- [ ] **Suite nightly** de detección de drift por proveedor.
- [ ] **Trace schema persistido** N días (según política de privacidad).
- [ ] **Tasa de flakiness** por suite monitorizada y < 2 %.
- [ ] **Audit trimestral** de reproducibilidad del pipeline completo.

## Por qué importa

Sin reproducibilidad, los gates de la [Tabla 4.2](./umbrales) pierden su poder de bloqueo:
- Un PR puede pasar el gate hoy y fallarlo mañana sin que el código cambie.
- Un incidente en producción no puede reproducirse en staging.
- Las auditorías de compliance (EU AI Act, ISO 42001) no pueden validar que el sistema entregado es el sistema evaluado.

La reproducibilidad no es perfección bit a bit: es **reproducibilidad estadística** bien gestionada. Mediana sobre N runs, IC95 sobre la cota inferior, suites separadas para reproducibilidad y drift. Con estas piezas, los gates vuelven a ser fiables.

## Referencias

- Manual QA AI v13 — Cap. 32 (Reproducibilidad y determinismo)
- [`modules/05-prompt-regression/src/variance_evaluator.py`](https://github.com/gonzaloMorenoc/ai-testing-lab/blob/main/modules/05-prompt-regression/src/variance_evaluator.py) — patrón canónico implementado
- [Tabla maestra de umbrales](./umbrales)
- [Modelo de madurez QA AI](./madurez)
