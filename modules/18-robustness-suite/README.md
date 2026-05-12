# 18 — robustness-suite

Capítulo 12 del Manual QA AI v13: **robustness y perturbation testing**, separado del red teaming.

## Por qué un módulo dedicado

El manual v13 separa explícitamente perturbation testing (Cap. 12) de red teaming (Cap. 7 y 14–15). Mezclarlos es un antipatrón documentado: **robustness mide estabilidad ante variaciones legítimas del input (typos, paráfrasis, code-mixing) y red teaming mide resistencia frente a ataques deliberadamente maliciosos**. Una métrica única para los dos esconde los modos de fallo de cada uno.

El módulo 07 del repo (`redteam-garak`) mezcla las dos cosas históricamente; este módulo separa la parte de robustness pura.

## Quickstart

```bash
pytest modules/18-robustness-suite/tests/ -q
```

```
52 passed in 0.07s
```

## API pública

| Símbolo | Tipo | Descripción |
|---|---|---|
| `PerturbationCategory` | StrEnum | 8 categorías (Tabla 12.1) |
| `PERTURBATION_SPECS` | dict | Especificación de las 11 perturbaciones implementadas |
| `PERTURBERS` | dict | Implementaciones funcionales `(query, rng) -> query'` |
| `apply(name, query, rng)` | función | Aplica perturbación nombrada |
| `RobustnessRunner` | clase | Ejecuta batería sobre chatbot mock |
| `RobustnessReport` | dataclass | Resultado agregado §12.3 |
| `consistency_score / semantic_stability / refusal_stability / accuracy_degradation` | funciones | 4 métricas canónicas |

## Las 8 categorías de perturbación

| Categoría | Ejemplo en este módulo | Impacto típico |
|---|---|---|
| Lexical | `inject_typos`, `remove_diacritics` | Bajo si embedder robusto; alto en BM25 |
| Morphological | `morph_number_swap` | Bajo en LLMs grandes; visible en clasificadores pequeños |
| Syntactic | `passive_voice` | Medio: puede alterar ranking del retriever |
| Lexico-semantic | `paraphrase` | Test clásico de generalización |
| Idiomatic | `lang_switch_token` | Crítica en sistemas multilingües |
| Length | `truncate`, `verbose` | Truncados ⇒ baja relevancia |
| Case/format | `uppercase`, `emojify` | Bajo en LLMs; alto en heurísticas regex |
| Adversarial subtle | `zero_width` | Engaña filtros y rompe tokenizers (NO es jailbreak) |

## Cómo se separa de red teaming

Verificado en `tests/test_robustness_vs_redteam.py`:

- **NO** hay payloads de jailbreak ni "DAN".
- **NO** hay prompts adversariales contra el modelo.
- Las perturbaciones se aplican al **input legítimo**, no al payload de un ataque.
- `adversarial_subtle` (zero-width, Unicode confusables) prueba **estabilidad del tokenizer**, no compromiso del modelo.

## Integración con qa_thresholds

Las métricas de robustness aparecen en la Tabla 4.2 raíz:

- `consistency_score ≥ 0.80` (target)
- `refusal_stability` debe mantenerse ≥ 0.95 (no documentado explícitamente como gate independiente, pero deriva del cap. 25)
- `accuracy_degradation ≤ 0.05` por perturbación

## Estructura

```
modules/18-robustness-suite/
├── conftest.py
├── src/
│   ├── perturbations.py        # 11 perturbadores en 8 categorías
│   ├── robustness_metrics.py   # 4 métricas + RobustnessReport
│   └── robustness_runner.py    # Runner E2E sobre chatbot mock
└── tests/                      # 52 tests
```

## Referencias

- Manual QA AI v13 — Cap. 12 (pp. 43–45), Tabla 12.1 (perturbaciones), Tabla 12.2 (herramientas)
- Ribeiro et al. (2020) — Beyond Accuracy: Behavioral Testing of NLP Models with CheckList
- Zhu et al. (2023) — PromptBench
- Morris et al. (2020) — TextAttack
