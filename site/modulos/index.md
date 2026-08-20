---
title: "Módulos"
aside: false
---

# Veinte módulos

Cada uno aísla un concepto y se ejecuta solo. No hay orden obligatorio: entra por la familia que necesites y sigue el hilo desde ahí.

<div class="mod-resumen">
  <div><strong>771</strong><span>tests</span></div>
  <div><strong>1,6 s</strong><span>la suite entera</span></div>
  <div><strong>97 %</strong><span>cobertura</span></div>
  <div><strong>0</strong><span>API keys</span></div>
</div>

<div class="mod-indice">

<div class="mod-familia">

<div class="mod-familia-cab"><em>I</em><h2>Métricas unitarias</h2><span>135 tests</span></div>

- <a href="./01-primer-eval"><b>01 — primer-eval</b><i>El primer <code>LLMTestCase</code> · AnswerRelevancy · Faithfulness</i></a><em>49</em>
- <a href="./02-ragas-basics"><b>02 — ragas-basics</b><i>Pipeline RAGAS · context precision · recall</i></a><em>10</em>
- <a href="./03-llm-as-judge"><b>03 — llm-as-judge</b><i>G-Eval · DAG Metric · position y verbosity bias</i></a><em>43</em>
- <a href="./14-embedding-eval"><b>14 — embedding-eval</b><i>Similitud coseno · centroid shift · regresión semántica</i></a><em>33</em>

</div>

<div class="mod-familia">

<div class="mod-familia-cab"><em>II</em><h2>Conversación y regresión</h2><span>92 tests</span></div>

- <a href="./04-multi-turn"><b>04 — multi-turn</b><i>ConversationalTestCase · KnowledgeRetention · 8 turnos</i></a><em>28</em>
- <a href="./05-prompt-regression"><b>05 — prompt-regression</b><i>PromptRegistry · RegressionChecker · z-test</i></a><em>42</em>
- <a href="./06-hallucination-lab"><b>06 — hallucination-lab</b><i>Extracción de claims · groundedness · negaciones</i></a><em>22</em>

</div>

<div class="mod-familia">

<div class="mod-familia-cab"><em>III</em><h2>Seguridad y safety</h2><span>75 tests</span></div>

- <a href="./07-redteam-garak"><b>07 — redteam-garak</b><i>42 attack prompts · DAN · many-shot · token manipulation</i></a><em>22</em>
- <a href="./08-redteam-deepteam"><b>08 — redteam-deepteam</b><i>OWASP Top 10 LLM 2025 · prompt injection · agencia</i></a><em>31</em>
- <a href="./09-guardrails"><b>09 — guardrails</b><i>Detección de PII · validación de salida · pipeline I/O</i></a><em>22</em>

</div>

<div class="mod-familia">

<div class="mod-familia-cab"><em>IV</em><h2>Producción</h2><span>161 tests</span></div>

- <a href="./10-agent-testing"><b>10 — agent-testing</b><i>Tool selection · trayectorias · AST-safe eval</i></a><em>37</em>
- <a href="./11-playwright-streaming"><b>11 — playwright-streaming</b><i>SSE streaming · E2E de chatbot · FastAPI mock</i></a><em>opt.</em>
- <a href="./12-observability"><b>12 — observability</b><i>OTel spans · <code>@trace</code> · latencia · error tracking</i></a><em>21</em>
- <a href="./13-drift-monitoring"><b>13 — drift-monitoring</b><i>KS test · PSI · bootstrap IC95 · alert rules</i></a><em>30</em>
- <a href="./15-cost-aware-qa"><b>15 — cost-aware-qa</b><i>Coste por consulta · regresión de gasto · trade-offs</i></a><em>73</em>

</div>

<div class="mod-familia">

<div class="mod-familia-cab"><em>V</em><h2>Disciplinas avanzadas</h2><span>308 tests</span></div>

- <a href="./16-retrieval-advanced"><b>16 — retrieval-advanced</b><i>HyDE · híbrido · reranking · NDCG, MRR y MAP</i></a><em>73</em>
- <a href="./17-chatbot-testing"><b>17 — chatbot-testing</b><i>Intención · escalado · tono · aislamiento de sesiones</i></a><em>60</em>
- <a href="./18-robustness-suite"><b>18 — robustness-suite</b><i>Perturbaciones · typos · robustez frente a ruido</i></a><em>52</em>
- <a href="./19-hitl-iaa"><b>19 — hitl-iaa</b><i>Cohen y Fleiss kappa · ICC · Krippendorff · tamaño muestral</i></a><em>55</em>
- <a href="./20-end-to-end-case"><b>20 — end-to-end-case</b><i>Chatbot regulado · gates · incidente · postmortem</i></a><em>68</em>

</div>

</div>

<div class="mod-pie">

**¿No sabes por dónde empezar?** La [guía de arranque](/guia/ruta) clasifica tu sistema en tres pasos y te dice qué módulos te tocan. Si prefieres la versión larga, está en el [manual](/manual), capítulo por capítulo.

</div>

::: tip Ejecutar un módulo suelto
```bash
pytest modules/01-primer-eval/tests/ -v -m "not slow"
```
El módulo 11 necesita `pytest-playwright` y se salta si no está instalado; por eso no cuenta tests en la tabla.
:::
