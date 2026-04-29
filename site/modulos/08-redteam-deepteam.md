---
title: "08 — redteam-deepteam"
---

# 08 — redteam-deepteam

OWASP Top 10 LLM 2025 y riesgos de agencia con DeepTeam.

<div class="module-layout">
<div class="module-main">

## Qué aprenderás

- Las 10 vulnerabilidades más críticas en LLMs según OWASP 2025
- Riesgos de agencia: qué pasa cuando el LLM puede ejecutar acciones
- Cómo usar DeepTeam para simular ataques estructurados
- La diferencia entre un ataque de prompt injection y un ataque de agencia

## OWASP Top 10 LLM 2025

1. **Prompt Injection** — instrucciones maliciosas en el input
2. **Insecure Output Handling** — output sin validar
3. **Training Data Poisoning** — datos de entrenamiento comprometidos
4. **Model Denial of Service** — inputs que saturan el modelo
5. **Supply Chain Vulnerabilities** — dependencias comprometidas
6. **Sensitive Information Disclosure** — filtración de datos
7. **Insecure Plugin Design** — plugins con permisos excesivos
8. **Excessive Agency** — el agente puede hacer demasiado
9. **Overreliance** — confiar en el output sin verificación
10. **Model Theft** — extracción del modelo vía queries

## Por qué importa

> Los agentes LLM que pueden ejecutar código o llamar APIs son especialmente vulnerables. Un ataque de prompt injection en un agente tiene consecuencias reales, no solo respuestas incorrectas.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">8</div>
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
pytest modules/08-redteam-deepteam/tests/ \
  -m "not slow and not redteam" -q
```

<div class="module-next">
  <div class="next-label">Siguiente →</div>
  <a href="/modulos/09-guardrails">09 — guardrails</a>
</div>

</div>
</div>
