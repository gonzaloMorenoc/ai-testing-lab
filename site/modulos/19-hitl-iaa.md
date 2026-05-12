---
title: "19 — hitl-iaa"
---

# 19 — hitl-iaa

Human-in-the-loop e inter-annotator agreement. Las métricas y protocolos que defienden la fiabilidad de tu golden dataset cuando interviene revisión humana.

## El problema

Has reunido a tres expertos del dominio para anotar 200 ejemplos. Tres semanas después tienes un golden dataset. ¿Es válido para usar como gate de release? Sin IAA medido, no se sabe. La métrica automática puede correlacionar perfectamente con el "consenso humano" — pero si ese consenso no existe (cada anotador puntuaba con su propio criterio), la métrica automática hereda el ruido.

El **Capítulo 31 del manual v13** documenta los cuatro coeficientes canónicos de IAA, el protocolo de calibración en seis fases, y el cálculo de tamaño muestral según el efecto a detectar.

## 4 métricas según el caso

| Métrica | Anotadores | Escala | Función del módulo |
|---|---|---|---|
| κ de Cohen | 2 | Categórica | `cohen_kappa(a, b)` |
| Fleiss κ | ≥3 | Categórica | `fleiss_kappa(annotations)` |
| α de Krippendorff | ≥2 | Cualquiera | `krippendorff_alpha_nominal(annotations)` |
| ICC(2,1) | ≥2 | Continua | `icc_2way_random(ratings)` |

```python
from iaa_metrics import cohen_kappa, assert_acceptable_iaa

result = cohen_kappa(annotator_a, annotator_b)
# IAAResult(value=0.78, interpretation="substantial", n_items=200, n_annotators=2)

# Gate del dataset: si el IAA cae por debajo de 0.667, raise.
# Para datasets críticos en alto riesgo: exigir ≥ 0.80.
assert_acceptable_iaa(result, high_risk=True)
```

## Umbrales canónicos (§31.2)

| Valor | Interpretación (Landis & Koch) |
|---|---|
| `< 0.41` | Pobre o moderado: recalibrar guidelines |
| `0.41 – 0.60` | Moderado |
| `0.61 – 0.80` | Substancial |
| `0.81 – 1.00` | Casi perfecto |

::: tip Umbral operativo
**Mínimo aceptable**: `≥ 0.667` (Krippendorff 2018). **Datasets críticos en dominio regulado**: `≥ 0.80`. Si tu IAA es menor, no uses el dataset como gate de release. Recalibra guidelines y vuelve a anotar.
:::

## Protocolo de calibración en 6 fases (§31.4)

```python
from calibration_protocol import run_calibration

report = run_calibration(
    n_pilot_items=30,           # 20-50 ítems con todos los anotadores
    pilot_iaa=0.55,             # IAA inicial bajo (esperado)
    after_discussion_iaa=0.70,  # debe mejorar tras discusión
    final_iaa=0.78,             # debe alcanzar target tras re-anotación
    target_iaa=0.70,
)
assert report.all_passed, f"Calibración falló en fase: {report.failed_phase}"
```

Las 6 fases:

1. **Guidelines**: rúbrica con criterios y ejemplos documentada.
2. **Pilot**: 20-50 ítems con todos los anotadores.
3. **Discussion**: resolver desacuerdos, refinar guidelines a v2.
4. **Re-annotation**: con guidelines v2, IAA debe alcanzar target.
5. **Certification**: cada anotador certificado si IAA personal ≥ 0.70 con consenso.
6. **Re-calibration**: trimestralmente sobre nuevo subconjunto, para detectar drift de criterios.

## Tamaño muestral (§31.6)

Para detectar diferencias entre dos sistemas con potencia estadística ≥ 0.8 y α = 0.05:

```python
from sample_size import EffectSize, recommend_sample_size, n_for_proportion_comparison

# Cohen's d aproximado
rec = recommend_sample_size(EffectSize.MEDIUM)
# paired_n=300, unpaired_n=500

# Comparación de proporciones (refusal_rate, pass_rate)
n = n_for_proportion_comparison(p1=0.95, p2=0.93, alpha=0.05, power=0.80)
# Devuelve el N mínimo según fórmula clásica
```

| Tamaño de efecto | Cohen's d | Pareadas | No pareadas |
|---|:---:|---:|---:|
| Grande | ≥ 0.5 | 100 | 200 |
| Medio | ≈ 0.3 | 300 | 500 |
| Pequeño | ≤ 0.1 | 1000 | 1500 |

## Cuándo usar HITL

El manual §31.1 lista las dimensiones donde HITL sigue siendo necesario, aunque las métricas automáticas cubran el 80–90 % del trabajo evaluativo:

- Adecuación cultural y matices regionales.
- Tono profesional y voz de marca.
- Sutileza de razonamiento (LLMs grandes a veces lo bordean sin que las métricas lo capten).
- Casos límite éticos: dilemas, contenido controvertido.
- Validación final pre-release de PRs con alto blast radius.

## Plataformas recomendadas (§31.5)

| Plataforma | Fortaleza |
|---|---|
| Argilla | Open-source, integrada con HuggingFace, IAA nativo |
| Label Studio | Muy flexible, plantillas para texto/imagen/audio |
| Prodigy | Comercial, fuerte en active learning |
| Scale / Surge / Toloka | Marketplaces con calibración previa |

## Por qué `raise` y no `assert`

Las validaciones de IAA en runtime usan `raise ValueError`, no `assert`. El manual §28.4 documenta el porqué: `assert` se desactiva con `python -O` o `PYTHONOPTIMIZE=1`, lo que dejaría pasar datasets sin IAA validado en producción.

## Referencias

- Manual QA AI v13 — Cap. 31 (pp. 87–88)
- Landis & Koch (1977) — Escala de interpretación de κ
- Krippendorff (2018) — Content Analysis, 4ª ed.
- Cicchetti (1994) — Interpretación de ICC
