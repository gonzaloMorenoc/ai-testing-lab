# Módulo 13 — Drift Monitoring

**Status:** implemented

## Objetivos

- Calcular PSI entre distribución de referencia y distribución actual
- Configurar reglas de alerta: caída de media, p95, PSI
- Componer múltiples reglas y detectar cuál disparó

## Cómo ejecutar

```bash
cd modules/13-drift-monitoring
pytest tests/ -m "not slow" -v
pytest tests/ -m slow -v   # requiere LANGFUSE_SECRET_KEY
```

## Ejercicio propuesto

Implementa un `DriftReport` que ejecute todas las reglas configuradas, incluya el PSI y genere un dict con timestamp, métricas y alertas disparadas.

Solución en `exercises/solutions/13-drift-monitoring-solution.py`.
