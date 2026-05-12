# Requisitos del módulo 19

## Dependencias

Solo stdlib. Para producción real, considerar:
- `scikit-learn` (`cohen_kappa_score`, `confusion_matrix`).
- `krippendorff` o `irrCAC` para implementaciones validadas de α.
- `pingouin` o `scipy` para ICC con confianza intervalar.

## Variables de entorno

Ninguna.

## Markers pytest

Ninguno especial; todos los tests son rápidos y deterministas.

## Cómo extenderlo

- Añadir métricas continuas (Pearson, Spearman, Kendall τ): nuevo archivo `continuous_metrics.py`.
- Plataformas de anotación (Argilla, Label Studio, Prodigy, Scale): ver §31.5 del manual.
- Active learning para reducir tamaño de anotación humano: integrar con un módulo nuevo.
