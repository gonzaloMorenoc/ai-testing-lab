# Requisitos del módulo 15

## Dependencias

Solo stdlib. Ningún paquete externo necesario para tests rápidos.

## Variables de entorno

Ninguna. Los precios se externalizan vía `load_prices_from_config(path)`,
que en proyectos reales debería apuntar a un secret manager (Vault, AWS,
GCP Secret Manager).

## Markers pytest

- `not slow` (por defecto): tests rápidos, sin llamadas externas.

## Cómo extenderlo

- Para añadir un modelo nuevo: editar `PRICE_PER_1K` en `src/price_config.py` o
  proveer un JSON externo y cargarlo con `load_prices_from_config(path)`.
- Para añadir un tipo de cambio nuevo: extender `ChangeType` y `DELTA_THRESHOLDS`
  en `src/cost_regression.py`.
