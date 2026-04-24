# Módulo 07 — Red Team con Garak

**Status:** implemented

## Objetivos

- Ejecutar una colección de prompts de ataque reales contra un `model_fn`
- Medir `hit_rate` global y por categoría (DAN, encoding, roleplay, crescendo, indirect injection)
- Producir reportes estructurados con veredicto por intento

## Cómo ejecutar

```bash
cd modules/07-redteam-garak
pytest tests/ -m "not slow" -v
# Scan real contra Groq (requiere GROQ_API_KEY)
pytest tests/ -m slow -v
```

## Ejercicio propuesto

Implementa un detector de "cede" más robusto que combine:
- Keyword matching (ya dado)
- Presencia de secuencias instructivas ("step 1", "first,")
- Longitud sospechosa (respuestas largas tras prompt de ataque)

Solución en `exercises/solutions/07-redteam-garak-solution.py`.
