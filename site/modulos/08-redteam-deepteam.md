# 08 — redteam-deepteam

**Concepto:** OWASP Top 10 LLM 2025 y riesgos de agencia con DeepTeam.

**Tests:** 8 · **Tiempo:** ~0.05s · **API key:** no necesaria

## Qué aprenderás

- Las 10 vulnerabilidades más críticas en LLMs según OWASP 2025
- Riesgos de agencia: qué pasa cuando el LLM puede ejecutar acciones
- Cómo usar DeepTeam para simular ataques estructurados
- La diferencia entre un ataque de prompt injection y un ataque de agencia

## Ejecutar

```bash
pytest modules/08-redteam-deepteam/tests/ -m "not slow and not redteam" -q
```

## OWASP Top 10 LLM 2025 cubierto

1. **Prompt Injection** — instrucciones maliciosas en el input
2. **Insecure Output Handling** — el output del LLM se usa sin validar
3. **Training Data Poisoning** — datos de entrenamiento comprometidos
4. **Model Denial of Service** — inputs que saturan el modelo
5. **Supply Chain Vulnerabilities** — dependencias comprometidas
6. **Sensitive Information Disclosure** — filtración de datos del sistema
7. **Insecure Plugin Design** — plugins con permisos excesivos
8. **Excessive Agency** — el agente puede hacer demasiado
9. **Overreliance** — confiar en el output sin verificación
10. **Model Theft** — extracción del modelo vía queries

## Por qué importa

Los agentes LLM que pueden ejecutar código, llamar APIs o modificar datos son especialmente vulnerables. Un ataque de prompt injection en un agente puede tener consecuencias reales, no solo respuestas incorrectas.
