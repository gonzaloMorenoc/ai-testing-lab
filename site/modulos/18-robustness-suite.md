---
title: "18 — robustness-suite"
---

# 18 — robustness-suite

Robustness y perturbation testing, separado del red teaming. El manual v13 los trata como dos disciplinas distintas y mezclarlas es un antipatrón.

## El problema

Tu RAG funciona bien sobre las queries del golden set. Los usuarios reales escriben:

- "qse es la politicz d devolucnes" (typos)
- "POLITICA DE DEVOLUCIONES" (mayúsculas)
- "qué pasa con esoo plz" (code-mixing ES/EN)
- "describe brevemente, lo más conciso posible, los términos legales aplicables a una posible devolución que yo, como cliente, podría plantearme" (verbose)

Todas estas variaciones son **legítimas**. Si tu chatbot solo responde bien a queries limpias, en producción degrada silenciosamente.

El **Capítulo 12 del manual v13** define el robustness testing como dimensión propia de calidad, distinta de red teaming. Robustness mide **estabilidad ante perturbaciones legítimas**. Red teaming mide **resistencia ante ataques deliberadamente maliciosos**.

## Las 8 categorías de perturbación

| Categoría | Ejemplos en el módulo | Impacto típico |
|---|---|---|
| Lexical | `inject_typos`, `remove_diacritics` | Bajo si embedder robusto; alto en BM25 |
| Morphological | `morph_number_swap` | Bajo en LLMs grandes |
| Syntactic | `passive_voice` | Medio; puede alterar ranking |
| Lexico-semantic | `paraphrase` | Test clásico de generalización |
| Idiomatic | `lang_switch_token` | Crítica multilingüe |
| Length | `truncate`, `verbose` | Coste / relevancia |
| Case/format | `uppercase`, `emojify` | Alto en heurísticas regex |
| Adversarial subtle | `zero_width` | Tokenizer y filtros (NO jailbreak) |

## 4 métricas canónicas (§12.3)

```python
from robustness_runner import RobustnessRunner

runner = RobustnessRunner(chatbot_answer=my_chatbot.answer)
report = runner.run(golden_queries)

assert report.consistency_score >= 0.80       # similitud media entre respuestas
assert report.semantic_stability >= 0.75      # % pares por encima del umbral
assert report.refusal_stability >= 0.95       # safety no cambia con perturbaciones
assert (
    report.accuracy_degradation is None
    or report.accuracy_degradation <= 0.05
)  # Answer Correctness no cae > 5 %
```

## La frontera con red teaming

Verificado en `tests/test_robustness_vs_redteam.py`:

::: warning No mezclar
- **NO** hay payloads de jailbreak en este módulo.
- **NO** hay prompts adversariales contra el modelo.
- `adversarial_subtle` (zero-width, Unicode confusables) prueba la **estabilidad del tokenizer**, no compromiso del modelo.
- Para tests adversariales contra el modelo, ver [módulo 07 (Garak)](./07-redteam-garak) y [módulo 08 (DeepTeam/OWASP)](./08-redteam-deepteam).
:::

## Reportes por segmento (§12.3)

Reportar siempre por segmento, no solo media global:

```python
from robustness_metrics import aggregate_by_segment

by_perturbation = aggregate_by_segment(
    results, segment_key=lambda r: r.perturbation_name
)
# {"uppercase": 0.92, "inject_typos": 0.75, "paraphrase": 0.81, ...}

by_language = aggregate_by_segment(
    results, segment_key=lambda r: r.metadata.get("lang", "es")
)
# {"es": 0.88, "en": 0.91, "pt": 0.79}
```

Una media global de 0.85 puede esconder que en portugués el sistema cae a 0.65 y el bot está roto para el 20 % de tu base de usuarios.

## Integración con CI/CD

El manual §12.6 recomienda:

- **PR**: smoke set perturbado de 20-50 queries con las perturbaciones más baratas (typos, mayúsculas). 1-2 min de tiempo de pipeline.
- **Pre-staging**: suite completa con las 11 perturbaciones. 5-10 min.
- **Shadow traffic**: muestreo continuo en producción de queries reales perturbadas, reportar `consistency_mean` por segmento.

## Referencias

- Manual QA AI v13 — Cap. 12 (pp. 43–45), Tablas 12.1 y 12.2
- Ribeiro et al. (2020) — CheckList
- Zhu et al. (2023) — PromptBench
- Morris et al. (2020) — TextAttack
