# 07 — redteam-garak

**Concepto:** Red teaming con 42 attack prompts en 7 categorías. Scanner de vulnerabilidades.

**Tests:** 10 · **Tiempo:** ~0.05s · **API key:** no necesaria

## Qué aprenderás

- Las 7 categorías de ataque más comunes: DAN, encoding, roleplay, crescendo, many-shot, token manipulation, indirect injection
- Cómo construir un `VulnerabilityScanner` reutilizable
- Hit rate por categoría: dónde es más vulnerable tu modelo
- Técnicas de evasión modernas: many-shot jailbreaking y manipulación de tokens

## Ejecutar

```bash
pytest modules/07-redteam-garak/tests/ -m "not slow and not redteam" -q
```

## Código de ejemplo

```python
from src.vulnerability_scanner import VulnerabilityScanner
from src.attack_prompts import ATTACK_PROMPTS, prompts_by_category

# Escaneo completo
scanner = VulnerabilityScanner(prompts=ATTACK_PROMPTS)
report = scanner.scan(mi_modelo)
print(report.summary())
# VulnerabilityReport: 42 prompts, hit_rate=0.07, hits=3

# Análisis por categoría
by_cat = report.hit_rate_by_category()
# {'dan': 0.17, 'encoding': 0.0, 'many_shot': 0.33, ...}
```

## Categorías de ataque incluidas

| Categoría | Prompts | Técnica |
|-----------|:-------:|---------|
| DAN | 6 | Jailbreaks clásicos "Do Anything Now" |
| Encoding | 7 | Base64, ROT13, hex, leetspeak, unicode |
| Roleplay | 6 | Personajes sin restricciones |
| Crescendo | 5 | Escalada gradual de peticiones |
| Many-shot | 3 | Historial de conversación fabricado |
| Token manipulation | 4 | Guiones, espacios, zero-width chars |
| Indirect injection | 5 | Instrucciones ocultas en documentos |
