# UX Site Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rediseñar el site VitePress con paleta Lab Green, hero renovado y páginas de módulo con sidebar de stats.

**Architecture:** CSS custom properties sobrescriben el tema VitePress por defecto. El hero se mejora con badge de stats y terminal mejorada. Las 14 páginas de módulo adoptan un layout de dos columnas (contenido + sidebar de stats) usando HTML nativo dentro de Markdown.

**Tech Stack:** VitePress 1.6.x, CSS custom properties, HTML in Markdown, Node.js

---

## File Structure

```
site/.vitepress/theme/          ← NUEVO directorio
  index.ts                      ← extiende DefaultTheme, importa CSS
  custom.css                    ← paleta + nav + bloques + layout módulos

site/public/
  logo.svg                      ← NUEVO icono microscopio verde

site/.vitepress/config.ts       ← añadir logo
site/index.md                   ← hero renovado + badge
site/modulos/01-primer-eval.md  ← layout con sidebar (8 tests, Básico)
site/modulos/02-ragas-basics.md ← layout con sidebar (11 tests, Básico)
site/modulos/03-llm-as-judge.md ← layout con sidebar (12 tests, Intermedio)
site/modulos/04-multi-turn.md   ← layout con sidebar (14 tests, Intermedio)
site/modulos/05-prompt-regression.md ← layout con sidebar (18 tests, Intermedio)
site/modulos/06-hallucination-lab.md ← layout con sidebar (12 tests, Intermedio)
site/modulos/07-redteam-garak.md     ← layout con sidebar (11 tests, Intermedio)
site/modulos/08-redteam-deepteam.md  ← layout con sidebar (8 tests, Intermedio)
site/modulos/09-guardrails.md        ← layout con sidebar (11 tests, Avanzado)
site/modulos/10-agent-testing.md     ← layout con sidebar (10 tests, Avanzado)
site/modulos/11-playwright-streaming.md ← layout con sidebar (requiere playwright)
site/modulos/12-observability.md     ← layout con sidebar (8 tests, Avanzado)
site/modulos/13-drift-monitoring.md  ← layout con sidebar (16 tests, Avanzado)
site/modulos/14-embedding-eval.md    ← layout con sidebar (15 tests, Avanzado)
```

---

## Task 1: Theme base — CSS custom properties y nav

**Files:**
- Create: `site/.vitepress/theme/index.ts`
- Create: `site/.vitepress/theme/custom.css`

- [ ] **Step 1: Crear `site/.vitepress/theme/index.ts`**

```bash
mkdir -p site/.vitepress/theme
```

Contenido del archivo:

```ts
import DefaultTheme from 'vitepress/theme'
import './custom.css'

export default DefaultTheme
```

- [ ] **Step 2: Crear `site/.vitepress/theme/custom.css`** con toda la paleta Lab Green

```css
/* =============================================
   PALETA LAB GREEN — VitePress custom theme
   ============================================= */

:root {
  /* Brand colors */
  --vp-c-brand-1: #16a34a;
  --vp-c-brand-2: #15803d;
  --vp-c-brand-3: #4ade80;
  --vp-c-brand-soft: #f0fdf4;

  /* Hero */
  --vp-home-hero-name-color: transparent;
  --vp-home-hero-name-background: linear-gradient(120deg, #14532d 30%, #16a34a);
  --vp-home-hero-image-background-image: radial-gradient(
    circle,
    #dcfce7 0%,
    #f0fdf4 60%
  );
  --vp-home-hero-image-filter: blur(44px);

  /* Buttons */
  --vp-button-brand-bg: #16a34a;
  --vp-button-brand-hover-bg: #15803d;
  --vp-button-brand-active-bg: #166534;
  --vp-button-brand-border: #16a34a;
  --vp-button-brand-hover-border: #15803d;
}

/* =============================================
   NAV
   ============================================= */

.VPNav {
  border-bottom: 1px solid #dcfce7 !important;
  background: rgba(240, 253, 244, 0.92) !important;
  backdrop-filter: blur(8px);
}

.VPNavBar .title {
  color: #14532d !important;
  font-weight: 700;
}

.VPNavBar .title:hover {
  color: #16a34a !important;
}

/* =============================================
   SIDEBAR
   ============================================= */

.VPSidebarItem.is-active > .item .link {
  color: #16a34a !important;
  font-weight: 600;
}

.VPSidebarItem.is-active > .item .indicator {
  background-color: #16a34a !important;
}

/* =============================================
   CÓDIGO INLINE
   ============================================= */

:not(pre) > code {
  background: #f0fdf4 !important;
  color: #15803d !important;
  border: 1px solid #dcfce7;
  border-radius: 4px;
  padding: 0.1em 0.35em;
  font-size: 0.875em;
}

/* =============================================
   BLOQUES DE CÓDIGO FENCED
   ============================================= */

div[class*='language-'] {
  background: #0d2818 !important;
  border: 1px solid #1a3d24;
  border-radius: 8px;
}

div[class*='language-'] code {
  color: #86efac !important;
  background: transparent !important;
  border: none;
  padding: 0;
  font-size: 0.875em;
}

div[class*='language-'] .shiki {
  background: #0d2818 !important;
}

/* Números de línea */
div[class*='language-'].line-numbers-mode .line-numbers {
  background: #0b2015 !important;
  border-right: 1px solid #1a3d24;
  color: #2d6a3f;
}

/* =============================================
   CUSTOM BLOCKS (tip, warning, etc.)
   ============================================= */

.custom-block.tip {
  border-color: #16a34a !important;
  background: #f0fdf4 !important;
}

.custom-block.tip .custom-block-title {
  color: #15803d !important;
}

.custom-block.info {
  border-color: #4ade80 !important;
  background: #f0fdf4 !important;
}

/* =============================================
   BADGE HERO
   ============================================= */

.hero-badge {
  display: inline-block;
  background: #dcfce7;
  border: 1px solid #86efac;
  color: #166534;
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.2rem 0.75rem;
  border-radius: 999px;
  margin-bottom: 1rem;
}

/* =============================================
   FEATURES (home page)
   ============================================= */

.VPFeature {
  border: 1px solid #dcfce7 !important;
  background: #f0fdf4 !important;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.VPFeature:hover {
  border-color: #86efac !important;
  box-shadow: 0 4px 16px #16a34a1a;
}

.VPFeature .title {
  color: #14532d !important;
}

.VPFeature .details {
  color: #166534 !important;
}

/* =============================================
   LAYOUT MÓDULOS — sidebar de stats
   ============================================= */

.module-layout {
  display: flex;
  gap: 2rem;
  align-items: flex-start;
  margin-top: 1.5rem;
}

.module-main {
  flex: 1;
  min-width: 0;
}

.module-sidebar {
  width: 180px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  position: sticky;
  top: calc(var(--vp-nav-height) + 1.5rem);
}

.stat-card {
  background: #f0fdf4;
  border: 1px solid #86efac;
  border-radius: 8px;
  padding: 0.6rem 0.5rem;
  text-align: center;
}

.stat-card.stat-ok {
  background: #dcfce7;
}

.stat-number {
  color: #16a34a;
  font-size: 1.5rem;
  font-weight: 900;
  line-height: 1;
  margin-bottom: 0.15rem;
}

.stat-number.level {
  font-size: 0.9rem;
  color: #15803d;
}

.stat-label {
  color: #166534;
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.module-sidebar div[class*='language-'] {
  font-size: 0.75rem;
  margin: 0;
}

.module-sidebar div[class*='language-'] code {
  font-size: 0.72rem !important;
}

.module-next {
  padding-top: 0.75rem;
  border-top: 1px solid #dcfce7;
}

.next-label {
  color: #6b7280;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.3rem;
}

.module-next a {
  color: #16a34a !important;
  font-weight: 600;
  font-size: 0.82rem;
  text-decoration: underline;
}

/* =============================================
   RESPONSIVE — módulos en móvil
   ============================================= */

@media (max-width: 768px) {
  .module-layout {
    flex-direction: column;
  }

  .module-sidebar {
    width: 100%;
    position: static;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .stat-card {
    flex: 1;
    min-width: 70px;
  }

  .module-next {
    width: 100%;
  }
}
```

- [ ] **Step 3: Verificar que el build pasa**

```bash
cd site && npm run build 2>&1 | tail -6
```

Esperado: `build complete in X.XXs` sin errores.

- [ ] **Step 4: Commit**

```bash
git add site/.vitepress/theme/
git commit -m "feat(site): add Lab Green theme — custom CSS + VitePress theme entry"
```

---

## Task 2: Logo SVG + config.ts

**Files:**
- Create: `site/public/logo.svg`
- Modify: `site/.vitepress/config.ts`

- [ ] **Step 1: Crear `site/public/logo.svg`**

Icono de microscopio simplificado en verde:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" fill="none">
  <!-- Ocular -->
  <rect x="12" y="2" width="8" height="5" rx="2" fill="#16a34a"/>
  <!-- Tubo del microscopio -->
  <rect x="14" y="7" width="4" height="10" rx="1" fill="#15803d"/>
  <!-- Brazo -->
  <rect x="8" y="14" width="12" height="3" rx="1.5" fill="#16a34a"/>
  <!-- Lente -->
  <circle cx="16" cy="20" r="4" fill="#4ade80" stroke="#16a34a" stroke-width="1.5"/>
  <!-- Base -->
  <rect x="6" y="26" width="20" height="3" rx="1.5" fill="#14532d"/>
  <!-- Pie del tubo -->
  <rect x="15" y="23" width="2" height="3" fill="#15803d"/>
</svg>
```

- [ ] **Step 2: Modificar `site/.vitepress/config.ts`** — añadir logo

Leer el archivo actual y añadir `logo` en `themeConfig`:

```ts
themeConfig: {
  logo: '/logo.svg',
  siteTitle: 'LLM Testing Lab',
  // ... resto igual
```

- [ ] **Step 3: Verificar build**

```bash
cd site && npm run build 2>&1 | tail -4
```

Esperado: `build complete` sin errores.

- [ ] **Step 4: Commit**

```bash
git add site/public/logo.svg site/.vitepress/config.ts
git commit -m "feat(site): add Lab Green logo SVG and wire to VitePress config"
```

---

## Task 3: Hero page renovada (site/index.md)

**Files:**
- Modify: `site/index.md`

- [ ] **Step 1: Reemplazar `site/index.md`** con el contenido completo:

```markdown
---
layout: home

hero:
  name: "LLM Testing Lab"
  text: "Testa tus LLMs como un profesional"
  tagline: "14 módulos pytest · RAG · red teaming · guardrails · observabilidad · drift. Sin API key. Sin conexión."
  image:
    src: /demo.svg
    alt: "142 tests pasando en 0.16s"
  actions:
    - theme: brand
      text: Empezar →
      link: /guia/instalacion
    - theme: alt
      text: Ver módulos
      link: /modulos/
    - theme: alt
      text: GitHub ↗
      link: https://github.com/gonzaloMorenoc/ai-testing-lab

features:
  - icon: 🔬
    title: Evaluación RAG completa
    details: Faithfulness, context precision y answer relevancy con RAGAS. LLM-as-judge con G-Eval y calibración de position bias. Embeddings coseno para regresión semántica.

  - icon: 🛡️
    title: Red teaming y seguridad
    details: 42 attack prompts en 7 categorías — DAN, encoding, many-shot, token manipulation e indirect injection. OWASP Top 10 LLM 2025. Guardrails de entrada y salida.

  - icon: 📡
    title: Observabilidad y drift
    details: Trazas OpenTelemetry con Langfuse y Phoenix. Detección de drift semántico con PSI y AlertHistory. Tendencias degrading / recovering / stable.

  - icon: ⚡
    title: Sin llamadas a APIs
    details: Todos los tests rápidos usan mocks deterministas — word overlap, embeddings con hashlib, AST-safe eval. La suite completa corre en 0.16s sin conexión.

  - icon: 🧩
    title: Módulos independientes
    details: Cada lab enseña exactamente un concepto. Puedes empezar por cualquier módulo según lo que necesites aprender o implementar en tu proyecto.

  - icon: 🐍
    title: pytest-nativo
    details: Si sabes pytest, ya sabes cómo ejecutar esto. Sin frameworks propietarios, sin CLIs especiales. Solo pytest y las librerías que ya conoces.
---

<div class="hero-badge">✓ 142 tests · 0.16s · sin API key</div>

## Quickstart

```bash
git clone https://github.com/gonzaloMorenoc/ai-testing-lab.git
cd ai-testing-lab
pip install deepeval pytest pytest-cov numpy
pytest modules/ -m "not slow and not redteam" -q
```

```
142 passed, 1 skipped in 0.16s
```

Sin API key. Sin cuenta de pago. Sin conexión a internet.

## Qué aprenderás

```
Pirámide de evaluación para LLMs
│
├── Métricas unitarias
│   ├── 01  LLMTestCase, AnswerRelevancy, Faithfulness
│   ├── 02  RAGAS: faithfulness, context_precision, context_recall
│   ├── 03  LLM-as-judge: G-Eval, calibración de position bias
│   └── 14  Similitud coseno, regression checker, centroid shift
│
├── Conversación y regresión
│   ├── 04  Multi-turn: ConversationalTestCase, memoria de 8 turnos
│   ├── 05  Regresión de prompts: PromptRegistry, z-test de significación
│   └── 06  Alucinaciones: extracción de claims, groundedness con negaciones
│
├── Seguridad y safety
│   ├── 07  Red teaming: 42 attack prompts, hit rate por categoría
│   ├── 08  DeepTeam: OWASP Top 10 LLM 2025, riesgos de agencia
│   └── 09  Guardrails: PII detection, pipeline de validación I/O
│
└── Producción
    ├── 10  Evaluación de agentes: tool accuracy, trayectorias
    ├── 11  E2E streaming: Playwright + SSE + FastAPI
    ├── 12  Observabilidad: OTel, Langfuse, Phoenix
    └── 13  Drift monitoring: PSI, AlertHistory, tendencias
```
```

- [ ] **Step 2: Verificar build**

```bash
cd site && npm run build 2>&1 | tail -4
```

Esperado: `build complete` sin errores.

- [ ] **Step 3: Commit**

```bash
git add site/index.md
git commit -m "feat(site): renovate hero page with Lab Green badge and improved tagline"
```

---

## Task 4: Módulos métricas unitarias (01, 02, 03, 14)

**Files:**
- Modify: `site/modulos/01-primer-eval.md`
- Modify: `site/modulos/02-ragas-basics.md`
- Modify: `site/modulos/03-llm-as-judge.md`
- Modify: `site/modulos/14-embedding-eval.md`

- [ ] **Step 1: Reemplazar `site/modulos/01-primer-eval.md`**

```markdown
---
title: "01 — primer-eval"
---

# 01 — primer-eval

Tu primer `LLMTestCase` con DeepEval. Métricas AnswerRelevancy y Faithfulness con mocks deterministas.

<div class="module-layout">
<div class="module-main">

## Qué aprenderás

- Estructura de un `LLMTestCase`: `input`, `actual_output`, `retrieval_context`
- Cómo funciona `AnswerRelevancy` por dentro (word overlap con la query)
- Cómo funciona `Faithfulness` (¿la respuesta se puede inferir del contexto?)
- Cuándo un test de evaluación debe pasar y cuándo debe fallar

## Código de ejemplo

```python
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
from deepeval.test_case import LLMTestCase

def test_respuesta_relevante_y_fiel():
    case = LLMTestCase(
        input="¿Cuál es la política de devoluciones?",
        actual_output="Puedes devolver cualquier producto en 30 días.",
        retrieval_context=["Política: devoluciones en 30 días desde la compra."],
    )
    assert_test(case, [
        AnswerRelevancyMetric(threshold=0.7),
        FaithfulnessMetric(threshold=0.7),
    ])
```

## Por qué importa

> Sin métricas, detectar regresiones en el prompt requiere revisión manual. Con `LLMTestCase` puedes automatizarlo en CI.

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
  <div class="stat-number level">Básico</div>
  <div class="stat-label">nivel</div>
</div>

```bash
pytest modules/01-primer-eval/tests/ \
  -m "not slow" -q
```

<div class="module-next">
  <div class="next-label">Siguiente →</div>
  <a href="/modulos/02-ragas-basics">02 — ragas-basics</a>
</div>

</div>
</div>
```

- [ ] **Step 2: Reemplazar `site/modulos/02-ragas-basics.md`**

```markdown
---
title: "02 — ragas-basics"
---

# 02 — ragas-basics

Evaluar un pipeline RAG completo con las métricas core de RAGAS.

<div class="module-layout">
<div class="module-main">

## Qué aprenderás

- Las tres métricas core de RAGAS: faithfulness, context precision y answer relevancy
- Cómo construir un `RAGASEvaluator` reutilizable
- La diferencia entre evaluar el retriever (context precision) y el generador (faithfulness)
- Cómo inyectar clusters de sinónimos de dominio para mejorar la precisión

## Código de ejemplo

```python
from src.ragas_evaluator import RAGASEvaluator, build_synonym_clusters

clusters = build_synonym_clusters(
    custom_clusters=[["devolución", "reembolso", "retorno"]],
)
evaluator = RAGASEvaluator(synonym_clusters=clusters)

result = evaluator.evaluate(
    query="¿Puedo devolver el producto?",
    context=["Aceptamos reembolsos en 30 días."],
    response="Sí, puedes solicitar un reembolso en 30 días.",
)
assert result["faithfulness"] > 0.8
assert result["answer_relevancy"] > 0.7
```

## Por qué importa

> Context precision y context recall miden cosas distintas: un retriever puede devolver muchos chunks relevantes (alto recall) pero también muchos irrelevantes (baja precision). RAGAS te permite diagnosticar exactamente cuál es el problema.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">11</div>
  <div class="stat-label">tests</div>
</div>

<div class="stat-card">
  <div class="stat-number">0.06s</div>
  <div class="stat-label">duración</div>
</div>

<div class="stat-card stat-ok">
  <div class="stat-number">✓</div>
  <div class="stat-label">sin API key</div>
</div>

<div class="stat-card">
  <div class="stat-number level">Básico</div>
  <div class="stat-label">nivel</div>
</div>

```bash
pytest modules/02-ragas-basics/tests/ \
  -m "not slow" -q
```

<div class="module-next">
  <div class="next-label">Siguiente →</div>
  <a href="/modulos/03-llm-as-judge">03 — llm-as-judge</a>
</div>

</div>
</div>
```

- [ ] **Step 3: Reemplazar `site/modulos/03-llm-as-judge.md`**

```markdown
---
title: "03 — llm-as-judge"
---

# 03 — llm-as-judge

Usar un LLM como juez con G-Eval y DAG Metric. Detectar y mitigar position bias.

<div class="module-layout">
<div class="module-main">

## Qué aprenderás

- Cómo funciona G-Eval: rúbrica personalizada → LLM puntúa de 0 a 1
- DAG Metric: lógica de evaluación compuesta (AND, OR) sin LLM juez
- Position bias: por qué el juez puntúa más alto la respuesta que aparece primero
- Cómo calibrar el position bias evaluando en ambos órdenes y promediando

## Código de ejemplo

```python
from src.geval_judge import GEvalJudge

judge = GEvalJudge()

# Calibración de position bias
result = judge.calibrate_for_position_bias(
    output_a="Respuesta A del modelo",
    output_b="Respuesta B del modelo",
    criteria="relevancia y precisión factual",
)
print(result["bias_delta"])        # diferencia entre orden A→B y B→A
print(result["calibrated_winner"]) # "A", "B" o "tie"
```

## Por qué importa

> Sin calibración, el 60-70% de las comparaciones A/B con LLM-as-judge están sesgadas hacia la posición. Esto invalida completamente los resultados de evaluación comparativa.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">12</div>
  <div class="stat-label">tests</div>
</div>

<div class="stat-card">
  <div class="stat-number">0.07s</div>
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
pytest modules/03-llm-as-judge/tests/ \
  -m "not slow" -q
```

<div class="module-next">
  <div class="next-label">Siguiente →</div>
  <a href="/modulos/14-embedding-eval">14 — embedding-eval</a>
</div>

</div>
</div>
```

- [ ] **Step 4: Reemplazar `site/modulos/14-embedding-eval.md`**

```markdown
---
title: "14 — embedding-eval"
---

# 14 — embedding-eval

Evaluar similitud semántica con embeddings. Regresión semántica y detección de drift a nivel de corpus.

<div class="module-layout">
<div class="module-main">

## Qué aprenderás

- `MockEmbeddingModel`: embeddings deterministas con hashlib para tests sin API
- `SemanticSimilarityMetric`: similitud coseno entre expected y actual output
- `EmbeddingRegressionChecker`: detectar si el candidato se aleja semánticamente del baseline
- `compute_centroid_shift`: medir drift semántico a nivel de corpus completo

## Código de ejemplo

```python
from src.embedding_evaluator import MockEmbeddingModel, SemanticSimilarityMetric
from src.semantic_drift import compute_centroid_shift, semantic_drift_alert

model = MockEmbeddingModel(dim=64)
metric = SemanticSimilarityMetric(model, threshold=0.7)

result = metric.measure(
    expected="El envío tarda entre 3 y 5 días laborables.",
    actual="Los pedidos se entregan en 3-5 días hábiles.",
)
print(result.similarity)  # ~0.85
print(result.passed)      # True

# Drift de corpus completo
shift = compute_centroid_shift(corpus_referencia, corpus_actual, model)
alert = semantic_drift_alert(model, threshold=0.1)
drift_result = alert(corpus_referencia, corpus_actual)
```

## Por qué importa

> Las métricas de overlap léxico no detectan paráfrasis. Si el modelo empieza a responder con sinónimos distintos a los del baseline, el drift semántico lo detecta aunque las palabras sean diferentes.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">15</div>
  <div class="stat-label">tests</div>
</div>

<div class="stat-card">
  <div class="stat-number">0.06s</div>
  <div class="stat-label">duración</div>
</div>

<div class="stat-card stat-ok">
  <div class="stat-number">✓</div>
  <div class="stat-label">sin API key</div>
</div>

<div class="stat-card">
  <div class="stat-number level">Avanzado</div>
  <div class="stat-label">nivel</div>
</div>

```bash
pytest modules/14-embedding-eval/tests/ \
  -m "not slow" -q
```

<div class="module-next">
  <div class="next-label">Fin del lab</div>
  <a href="/modulos/">← Ver todos</a>
</div>

</div>
</div>
```

- [ ] **Step 5: Verificar build**

```bash
cd site && npm run build 2>&1 | tail -4
```

Esperado: `build complete` sin errores.

- [ ] **Step 6: Commit**

```bash
git add site/modulos/01-primer-eval.md site/modulos/02-ragas-basics.md \
        site/modulos/03-llm-as-judge.md site/modulos/14-embedding-eval.md
git commit -m "feat(site): add sidebar layout to metrics modules (01, 02, 03, 14)"
```

---

## Task 5: Módulos conversación y regresión (04, 05, 06)

**Files:**
- Modify: `site/modulos/04-multi-turn.md`
- Modify: `site/modulos/05-prompt-regression.md`
- Modify: `site/modulos/06-hallucination-lab.md`

- [ ] **Step 1: Reemplazar `site/modulos/04-multi-turn.md`**

```markdown
---
title: "04 — multi-turn"
---

# 04 — multi-turn

Testear conversaciones de múltiples turnos y retención de información entre turnos.

<div class="module-layout">
<div class="module-main">

## Qué aprenderás

- `ConversationalTestCase` y cómo estructurar tests de diálogo
- Por qué el tamaño de la ventana de contexto importa (configurado en 8 turnos)
- Cómo verificar que la información del turno 1 sigue disponible en el turno 9
- Detección de contradicciones entre turnos

## Código de ejemplo

```python
from src.multi_turn_rag import MultiTurnRAG

rag = MultiTurnRAG()
rag.respond("¿Cuál es la política de devoluciones?")  # turno 1

# 7 turnos sobre otro tema...
for _ in range(7):
    rag.respond("¿Cuánto tarda el envío?")

# El turno 9 debe recordar el turno 1
response = rag.respond("¿Qué me dijiste sobre las devoluciones?")
assert "30 días" in response or "devolución" in response.lower()
```

## Por qué importa

> Un sistema RAG con ventana de contexto pequeña "olvida" información relevante a medida que avanza la conversación. El usuario siente que el sistema no le presta atención.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">14</div>
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
pytest modules/04-multi-turn/tests/ \
  -m "not slow" -q
```

<div class="module-next">
  <div class="next-label">Siguiente →</div>
  <a href="/modulos/05-prompt-regression">05 — prompt-regression</a>
</div>

</div>
</div>
```

- [ ] **Step 2: Reemplazar `site/modulos/05-prompt-regression.md`**

```markdown
---
title: "05 — prompt-regression"
---

# 05 — prompt-regression

Detectar regresiones de calidad cuando cambias un prompt. Significación estadística con z-test.

<div class="module-layout">
<div class="module-main">

## Qué aprenderás

- `PromptRegistry`: versionar prompts como código con hash
- `RegressionChecker`: comparar dos versiones de un prompt sobre el mismo dataset
- z-test de una proporción para saber si la diferencia es estadísticamente significativa
- Cuándo una mejora del 3% importa y cuándo no

## Código de ejemplo

```python
from src.regression_checker import RegressionChecker, is_significant

checker = RegressionChecker()
delta = checker.compare(baseline_scores, candidate_scores)

if is_significant(delta, n_samples=200, baseline_score=0.75):
    print(f"Mejora real: +{delta:.1%}")
else:
    print("Diferencia dentro del ruido estadístico")
```

## Por qué importa

> Sin test estadístico, una mejora del 2% con 20 muestras parece real pero puede ser ruido. Un z-test te dice si necesitas más datos o si el resultado es conclusivo.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">18</div>
  <div class="stat-label">tests</div>
</div>

<div class="stat-card">
  <div class="stat-number">0.06s</div>
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
pytest modules/05-prompt-regression/tests/ \
  -m "not slow" -q
```

<div class="module-next">
  <div class="next-label">Siguiente →</div>
  <a href="/modulos/06-hallucination-lab">06 — hallucination-lab</a>
</div>

</div>
</div>
```

- [ ] **Step 3: Reemplazar `site/modulos/06-hallucination-lab.md`**

```markdown
---
title: "06 — hallucination-lab"
---

# 06 — hallucination-lab

Detectar alucinaciones a nivel de claim individual. Groundedness con detección de negaciones.

<div class="module-layout">
<div class="module-main">

## Qué aprenderás

- Extracción de claims: descomponer una respuesta en afirmaciones verificables
- Groundedness: ¿cada claim está respaldado por el contexto?
- Detección de negaciones: "las devoluciones NO están permitidas" contradice el contexto
- La diferencia entre alucinación (información inventada) y contradicción (negar lo que dice el contexto)

## Código de ejemplo

```python
from src.groundedness_checker import GroundednessChecker

checker = GroundednessChecker(overlap_threshold=0.4)
context = "Las devoluciones están permitidas en 30 días."

# Claim que contradice el contexto
assert not checker.is_grounded(
    "Las devoluciones NO están permitidas.", context
)

# Claim respaldado por el contexto
assert checker.is_grounded(
    "Se puede devolver en 30 días.", context
)
```

## Por qué importa

> La mayoría de métricas de faithfulness no detectan negaciones explícitas. Un modelo que dice "No tienes derecho a devoluciones" cuando el contexto dice que sí las hay pasa los filtros de overlap léxico estándar.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">12</div>
  <div class="stat-label">tests</div>
</div>

<div class="stat-card">
  <div class="stat-number">0.06s</div>
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
pytest modules/06-hallucination-lab/tests/ \
  -m "not slow" -q
```

<div class="module-next">
  <div class="next-label">Siguiente →</div>
  <a href="/modulos/07-redteam-garak">07 — redteam-garak</a>
</div>

</div>
</div>
```

- [ ] **Step 4: Verificar build**

```bash
cd site && npm run build 2>&1 | tail -4
```

Esperado: `build complete` sin errores.

- [ ] **Step 5: Commit**

```bash
git add site/modulos/04-multi-turn.md site/modulos/05-prompt-regression.md \
        site/modulos/06-hallucination-lab.md
git commit -m "feat(site): add sidebar layout to conversation modules (04, 05, 06)"
```

---

## Task 6: Módulos seguridad (07, 08, 09)

**Files:**
- Modify: `site/modulos/07-redteam-garak.md`
- Modify: `site/modulos/08-redteam-deepteam.md`
- Modify: `site/modulos/09-guardrails.md`

- [ ] **Step 1: Reemplazar `site/modulos/07-redteam-garak.md`**

```markdown
---
title: "07 — redteam-garak"
---

# 07 — redteam-garak

Red teaming con 42 attack prompts en 7 categorías. Scanner de vulnerabilidades automatizado.

<div class="module-layout">
<div class="module-main">

## Qué aprenderás

- Las 7 categorías de ataque más comunes: DAN, encoding, roleplay, crescendo, many-shot, token manipulation, indirect injection
- Cómo construir un `VulnerabilityScanner` reutilizable
- Hit rate por categoría: dónde es más vulnerable tu modelo
- Técnicas de evasión modernas: many-shot jailbreaking y manipulación de tokens

## Código de ejemplo

```python
from src.vulnerability_scanner import VulnerabilityScanner
from src.attack_prompts import ATTACK_PROMPTS

scanner = VulnerabilityScanner(prompts=ATTACK_PROMPTS)
report = scanner.scan(mi_modelo)
print(report.summary())
# VulnerabilityReport: 42 prompts, hit_rate=0.07, hits=3

by_cat = report.hit_rate_by_category()
# {'dan': 0.17, 'encoding': 0.0, 'many_shot': 0.33, ...}
```

## Categorías incluidas

| Categoría | Prompts | Técnica |
|-----------|:-------:|---------|
| DAN | 6 | Jailbreaks "Do Anything Now" |
| Encoding | 7 | Base64, ROT13, hex, leetspeak |
| Roleplay | 6 | Personajes sin restricciones |
| Crescendo | 5 | Escalada gradual |
| Many-shot | 3 | Historial fabricado |
| Token manip. | 4 | Guiones, zero-width chars |
| Indirect inj. | 5 | Instrucciones en documentos |

## Por qué importa

> Un modelo con hit rate > 30% necesita guardrails antes de ir a producción. Este módulo te da la línea base para medirlo.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">11</div>
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
pytest modules/07-redteam-garak/tests/ \
  -m "not slow and not redteam" -q
```

<div class="module-next">
  <div class="next-label">Siguiente →</div>
  <a href="/modulos/08-redteam-deepteam">08 — redteam-deepteam</a>
</div>

</div>
</div>
```

- [ ] **Step 2: Reemplazar `site/modulos/08-redteam-deepteam.md`**

```markdown
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
```

- [ ] **Step 3: Reemplazar `site/modulos/09-guardrails.md`**

```markdown
---
title: "09 — guardrails"
---

# 09 — guardrails

Validación de entrada y salida con Guardrails AI y NeMo Guardrails.

<div class="module-layout">
<div class="module-main">

## Qué aprenderás

- Pipeline de validación I/O: qué validar antes de llamar al LLM y después
- Detección de PII (información personal identificable) en inputs y outputs
- Rails conversacionales con NeMo Guardrails (Colang DSL)
- Cuándo usar guardrails de reglas vs guardrails basados en LLM

## Código de ejemplo

```python
from src.guardrail_pipeline import GuardrailPipeline

pipeline = GuardrailPipeline()
result = pipeline.run(
    user_input="Mi email es usuario@ejemplo.com. ¿Cuál es mi saldo?",
)

print(result.blocked)    # True — PII detectada en el input
print(result.reason)     # "pii_detected"
print(result.pii_found)  # ["usuario@ejemplo.com"]
```

## Por qué importa

> Sin guardrails, los usuarios pueden enviar datos sensibles que el LLM procesa y potencialmente incluye en respuestas a otros usuarios.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">11</div>
  <div class="stat-label">tests</div>
</div>

<div class="stat-card">
  <div class="stat-number">0.06s</div>
  <div class="stat-label">duración</div>
</div>

<div class="stat-card stat-ok">
  <div class="stat-number">✓</div>
  <div class="stat-label">sin API key</div>
</div>

<div class="stat-card">
  <div class="stat-number level">Avanzado</div>
  <div class="stat-label">nivel</div>
</div>

```bash
pytest modules/09-guardrails/tests/ \
  -m "not slow" -q
```

<div class="module-next">
  <div class="next-label">Siguiente →</div>
  <a href="/modulos/10-agent-testing">10 — agent-testing</a>
</div>

</div>
</div>
```

- [ ] **Step 4: Verificar build**

```bash
cd site && npm run build 2>&1 | tail -4
```

Esperado: `build complete` sin errores.

- [ ] **Step 5: Commit**

```bash
git add site/modulos/07-redteam-garak.md site/modulos/08-redteam-deepteam.md \
        site/modulos/09-guardrails.md
git commit -m "feat(site): add sidebar layout to security modules (07, 08, 09)"
```

---

## Task 7: Módulos producción (10, 11, 12, 13)

**Files:**
- Modify: `site/modulos/10-agent-testing.md`
- Modify: `site/modulos/11-playwright-streaming.md`
- Modify: `site/modulos/12-observability.md`
- Modify: `site/modulos/13-drift-monitoring.md`

- [ ] **Step 1: Reemplazar `site/modulos/10-agent-testing.md`**

```markdown
---
title: "10 — agent-testing"
---

# 10 — agent-testing

Evaluar agentes LLM: selección de herramientas, trayectorias y evaluación segura de expresiones.

<div class="module-layout">
<div class="module-main">

## Qué aprenderás

- Tool accuracy: ¿el agente selecciona la herramienta correcta para cada query?
- Trajectory evaluation: ¿el agente llega al resultado correcto por el camino correcto?
- AST-safe eval: cómo evaluar expresiones matemáticas sin `eval()` inseguro
- `AgentGoalAccuracy`: ¿el agente completó el objetivo del usuario?

## Código de ejemplo

```python
from src.simple_agent import SimpleAgent

agent = SimpleAgent()
result = agent.run("Calcula 15 * 23 + 47")

# Verificar la trayectoria
assert result.trajectory[0].tool == "calculate"
assert result.trajectory[0].result == "392"
assert result.final_output == "392"
```

El `calculate` interno usa un evaluador AST puro — sin `eval()`, sin acceso a builtins, sin riesgo de inyección de código.

## Por qué importa

> Los tests de agentes deben verificar no solo el resultado final sino también el proceso. Un agente que llega al resultado correcto por el camino equivocado no es un agente fiable.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">10</div>
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
  <div class="stat-number level">Avanzado</div>
  <div class="stat-label">nivel</div>
</div>

```bash
pytest modules/10-agent-testing/tests/ \
  -m "not slow" -q
```

<div class="module-next">
  <div class="next-label">Siguiente →</div>
  <a href="/modulos/11-playwright-streaming">11 — playwright-streaming</a>
</div>

</div>
</div>
```

- [ ] **Step 2: Reemplazar `site/modulos/11-playwright-streaming.md`**

```markdown
---
title: "11 — playwright-streaming"
---

# 11 — playwright-streaming

Tests E2E de interfaces de chatbot con streaming SSE usando Playwright.

<div class="module-layout">
<div class="module-main">

## Qué aprenderás

- Cómo testear Server-Sent Events (SSE) con Playwright
- Montar un servidor mock de FastAPI para simular un chatbot en streaming
- Verificar que los tokens llegan en orden y sin corrupción
- Tests de regresión visual para UIs de chat

## Requisitos adicionales

```bash
pip install playwright pytest-playwright fastapi uvicorn
playwright install chromium
```

## Código de ejemplo

```python
async def test_streaming_completa_sin_errores(page):
    await page.goto("http://localhost:8765")
    await page.fill("#input", "¿Cuánto tarda el envío?")
    await page.click("#send")

    await page.wait_for_selector(".message.complete")
    content = await page.text_content(".message.assistant")
    assert len(content) > 10
    assert "error" not in content.lower()
```

## Por qué importa

> El streaming SSE tiene comportamientos que los tests de API no detectan: tokens fuera de orden, cortes en mitad de una palabra, o buffers que no se vacían correctamente.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">8+</div>
  <div class="stat-label">tests</div>
</div>

<div class="stat-card">
  <div class="stat-number">E2E</div>
  <div class="stat-label">duración</div>
</div>

<div class="stat-card">
  <div class="stat-number">⚙</div>
  <div class="stat-label">playwright</div>
</div>

<div class="stat-card">
  <div class="stat-number level">Avanzado</div>
  <div class="stat-label">nivel</div>
</div>

```bash
pip install playwright
playwright install chromium
pytest modules/11-playwright-streaming/tests/
```

<div class="module-next">
  <div class="next-label">Siguiente →</div>
  <a href="/modulos/12-observability">12 — observability</a>
</div>

</div>
</div>
```

- [ ] **Step 3: Reemplazar `site/modulos/12-observability.md`**

```markdown
---
title: "12 — observability"
---

# 12 — observability

Instrumentar un pipeline LLM con OpenTelemetry. Trazas, latencia y error tracking.

<div class="module-layout">
<div class="module-main">

## Qué aprenderás

- Cómo crear spans OTel para cada etapa del pipeline (retrieval, generation, reranking)
- El decorador `@trace` para instrumentar funciones automáticamente
- Cómo conectar a Langfuse y Phoenix para visualizar trazas
- Métricas de latencia: dónde se pierde tiempo en el pipeline

## Código de ejemplo

```python
from src.tracer import trace, get_collector

@trace("retrieval")
def retrieve(query: str) -> list[str]:
    return buscar_en_vector_db(query)

@trace("generation")
def generate(query: str, context: list[str]) -> str:
    return llamar_llm(query, context)

with get_collector() as collector:
    respuesta = generate("¿Cuál es la política?", retrieve("política"))
    assert collector.span_count == 2
    assert collector.total_latency < 5.0
```

## Por qué importa

> Sin observabilidad, cuando el sistema es lento no sabes si el problema está en el retriever, en el reranker o en la llamada al LLM.

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

<div class="stat-card">
  <div class="stat-number">opt.</div>
  <div class="stat-label">API key</div>
</div>

<div class="stat-card">
  <div class="stat-number level">Avanzado</div>
  <div class="stat-label">nivel</div>
</div>

```bash
pytest modules/12-observability/tests/ \
  -m "not slow" -q
```

<div class="module-next">
  <div class="next-label">Siguiente →</div>
  <a href="/modulos/13-drift-monitoring">13 — drift-monitoring</a>
</div>

</div>
</div>
```

- [ ] **Step 4: Reemplazar `site/modulos/13-drift-monitoring.md`**

```markdown
---
title: "13 — drift-monitoring"
---

# 13 — drift-monitoring

Detectar degradación de calidad en producción con PSI, AlertHistory y reglas de alerta.

<div class="module-layout">
<div class="module-main">

## Qué aprenderás

- PSI (Population Stability Index): cuándo la distribución de scores ha cambiado significativamente
- `AlertHistory`: rastrear tendencias a lo largo del tiempo (degrading / recovering / stable)
- Reglas de alerta: mean drop, p95, PSI threshold configurable
- Cómo combinar varias reglas con `evaluate_rules()`

## Código de ejemplo

```python
from src.drift_detector import compute_psi
from src.alert_rules import AlertHistory, mean_drop_alert, psi_alert, evaluate_rules

psi = compute_psi(scores_referencia, scores_actuales)

rules = [
    mean_drop_alert(reference_mean=0.85, threshold_pct=0.1),
    psi_alert(threshold=0.2),
]
results = evaluate_rules(rules, scores_actuales)

history = AlertHistory("calidad_global")
for result in results:
    history.add(result)

print(history.trend)        # "degrading", "recovering" o "stable"
print(history.trigger_rate) # fracción de checks que activaron alerta
```

## Interpretación del PSI

| PSI | Interpretación |
|-----|---------------|
| < 0.1 | Sin cambio significativo |
| 0.1 – 0.2 | Cambio moderado, investigar |
| > 0.2 | Cambio significativo, actuar |

## Por qué importa

> En producción, los LLMs se degradan silenciosamente. Sin monitorización, lo detectas cuando los usuarios se quejan.

</div>
<div class="module-sidebar">

<div class="stat-card">
  <div class="stat-number">16</div>
  <div class="stat-label">tests</div>
</div>

<div class="stat-card">
  <div class="stat-number">0.09s</div>
  <div class="stat-label">duración</div>
</div>

<div class="stat-card stat-ok">
  <div class="stat-number">✓</div>
  <div class="stat-label">sin API key</div>
</div>

<div class="stat-card">
  <div class="stat-number level">Avanzado</div>
  <div class="stat-label">nivel</div>
</div>

```bash
pytest modules/13-drift-monitoring/tests/ \
  -m "not slow" -q
```

<div class="module-next">
  <div class="next-label">Siguiente →</div>
  <a href="/modulos/14-embedding-eval">14 — embedding-eval</a>
</div>

</div>
</div>
```

- [ ] **Step 5: Verificar build**

```bash
cd site && npm run build 2>&1 | tail -4
```

Esperado: `build complete` sin errores.

- [ ] **Step 6: Commit**

```bash
git add site/modulos/10-agent-testing.md site/modulos/11-playwright-streaming.md \
        site/modulos/12-observability.md site/modulos/13-drift-monitoring.md
git commit -m "feat(site): add sidebar layout to production modules (10, 11, 12, 13)"
```

---

## Task 8: Verificación final y push

**Files:** ninguno nuevo

- [ ] **Step 1: Build completo limpio**

```bash
cd site && npm run build 2>&1
```

Esperado: `build complete in X.XXs` con 0 errores y 0 dead links.

- [ ] **Step 2: Verificar que no hay links rotos**

```bash
cd site && npm run build 2>&1 | grep -i "dead\|not found\|error" || echo "Sin errores de links"
```

Esperado: `Sin errores de links`

- [ ] **Step 3: Push al remoto**

```bash
git push origin main
```

Esperado: confirmación de push sin errores. Vercel desplegará automáticamente al detectar el push.

- [ ] **Step 4: Verificar deploy en Vercel**

Esperar ~60s y abrir la URL del deploy de Vercel para confirmar que el site se ve con la paleta Lab Green, el hero renovado y el sidebar de stats en las páginas de módulo.
