# 19 — hitl-iaa

Capítulo 31 del Manual QA AI v13: **Human-in-the-loop e inter-annotator agreement**. Métricas IAA canónicas (κ Cohen, κ Fleiss, α Krippendorff, ICC) + protocolo de calibración de 6 fases + cálculo de tamaño muestral.

## Quickstart

```bash
pytest modules/19-hitl-iaa/tests/ -q
```

```
55 passed in 0.06s
```

## Por qué un módulo dedicado

Las métricas automáticas (RAGAS, LLM-as-Judge) cubren ~80–90 % de la evaluación, pero ciertas dimensiones — adecuación cultural, tono profesional, sutileza de razonamiento, casos límite éticos — siguen requiriendo juicio humano experto. Sin un IAA documentado, esas anotaciones no son reproducibles y el golden dataset queda sin defender.

## API pública

| Símbolo | Tipo | Descripción |
|---|---|---|
| `cohen_kappa(a, b)` | función | κ de Cohen para 2 anotadores categóricos |
| `fleiss_kappa(annotations)` | función | Fleiss κ para ≥3 anotadores |
| `krippendorff_alpha_nominal(annotations)` | función | α de Krippendorff nominal (admite missing) |
| `icc_2way_random(ratings)` | función | ICC(2,1) para anotaciones continuas |
| `interpret_kappa(value)` | función | Landis & Koch: poor/fair/moderate/substantial/almost_perfect |
| `assert_acceptable_iaa(result, high_risk)` | función | Eleva `ValueError` si IAA < umbral (raise, no assert) |
| `MIN_ACCEPTABLE_KAPPA` | constante | 0.667 (estándar) |
| `HIGH_RISK_KAPPA` | constante | 0.80 (dominios regulados) |
| `run_calibration(...)` | función | Protocolo §31.4 simulado en 6 fases |
| `recommend_sample_size(effect_size, paired)` | función | Tamaño muestral por Cohen's d |
| `n_for_proportion_comparison(p1, p2, alpha, power)` | función | Tamaño muestral para Chi²/Fisher |

## Cuándo usar cada métrica

| Métrica | Anotadores | Escala | Cuándo |
|---|---|---|---|
| κ de Cohen | 2 | Categórica | Caso más común con 2 jueces |
| κ ponderado | 2 | Ordinal | Categorías con orden natural (no implementado aquí; usar scipy) |
| Fleiss κ | ≥3 | Categórica | Igual a Cohen pero con N anotadores |
| α de Krippendorff | ≥2 | Cualquiera | Permite missing values; estándar moderno |
| ICC(2,1) | ≥2 | Continua | Puntuaciones numéricas (1–5, 0–100) |

## Umbrales canónicos (Manual §31.2)

- `< 0.61`: pobre o moderado → recalibrar guidelines y reentrenar anotadores.
- `≥ 0.667`: aceptable (Krippendorff 2018).
- `≥ 0.81`: casi perfecto (Landis & Koch 1977).
- **Datasets críticos en alto riesgo: exigir ≥ 0.80**.

## Estructura

```
modules/19-hitl-iaa/
├── conftest.py
├── src/
│   ├── iaa_metrics.py            # κ Cohen, Fleiss, α Krippendorff, ICC
│   ├── calibration_protocol.py   # Protocolo de 6 fases (§31.4)
│   └── sample_size.py            # Recomendaciones §31.6
└── tests/                        # 55 tests, marcador not slow
```

## Referencias

- Manual QA AI v13 — Cap. 31 (pp. 87–88)
- Landis & Koch (1977) — escala de interpretación de κ
- Krippendorff (2018) — Content Analysis 4th ed.
- Cicchetti (1994) — ICC interpretation
- §28.4 — `raise ValueError` en lugar de `assert` para sobrevivir a `python -O`
