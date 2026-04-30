---
title: "07 — redteam-garak"
---

# 07 — redteam-garak

Red teaming con 42 attack prompts en 7 categorías. Scanner de vulnerabilidades automatizado.

<div class="module-layout">
<div class="module-main">

## Qué aprenderás

- Las 7 categorías de ataque más comunes: DAN, encoding, roleplay, crescendo, many-shot, token manipulation, indirect injection
- Cómo construir un `VulnerabilityScanner` reutilizable
- Hit rate por categoría: dónde es más vulnerable tu modelo
- Técnicas de evasión modernas: many-shot jailbreaking y manipulación de tokens

## Código de ejemplo

```python
from src.vulnerability_scanner import VulnerabilityScanner
from src.attack_prompts import ATTACK_PROMPTS

scanner = VulnerabilityScanner(prompts=ATTACK_PROMPTS)
report = scanner.scan(mi_modelo)
print(report.summary())
# VulnerabilityReport: 42 prompts, hit_rate=0.07, hits=3

by_cat = report.hit_rate_by_category()
# {'dan': 0.17, 'encoding': 0.0, 'many_shot': 0.33, ...}
```

## Categorías incluidas

| Categoría | Prompts | Técnica |
|-----------|:-------:|---------|
| DAN | 6 | Jailbreaks "Do Anything Now" |
| Encoding | 7 | Base64, ROT13, hex, leetspeak |
| Roleplay | 6 | Personajes sin restricciones |
| Crescendo | 5 | Escalada gradual |
| Many-shot | 3 | Historial fabricado |
| Token manip. | 4 | Guiones, zero-width chars |
| Indirect inj. | 5 | Instrucciones en documentos |

## Nuevas implementaciones (Manual QA AI v12)

**`RobustnessSuite`** — batería de 7 perturbaciones (§9.5) para medir consistencia bajo variaciones del input:

```python
from src.robustness_suite import run_robustness_suite

golden_queries = ["¿Cuál es la política de devoluciones?", "¿Cuánto tarda el envío?"]
report = run_robustness_suite(mi_chatbot, golden_queries)
# report.consistency_mean: float
# report.passed = consistency_mean >= 0.80
# report.results: list[PerturbationResult] — una por perturbación
```

| Perturbación | Ejemplo |
|-------------|---------|
| `typos` | política → politica |
| `uppercase` | POLÍTICA DE DEVOLUCIONES |
| `paraphrase` | reordenación de palabras |
| `lang_switch` | mezcla español/inglés |
| `whitespace` | espacios extra |
| `emoji` | 📦 política devoluciones |
| `truncate` | cortar al 70% del texto |

Gate de CI: `consistency_mean ≥ 0.80` (similitud BoW coseno, sin embeddings).

## Por qué importa

> Un modelo con hit rate > 30% necesita guardrails antes de ir a producción. Este módulo te da la línea base para medirlo.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">11</div>
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
