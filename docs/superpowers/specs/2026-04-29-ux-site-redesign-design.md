# UX Site Redesign — Design Spec

> **For agentic workers:** Use superpowers:executing-plans or superpowers:subagent-driven-development to implement the plan derived from this spec.

**Goal:** Rediseñar el site VitePress de ai-testing-lab con paleta Lab Green, hero renovado y páginas de módulo con sidebar de stats — todo en Markdown + CSS, sin componentes Vue.

**Approach:** Opción B — CSS custom + restructura de archivos Markdown. Dos archivos nuevos (`theme/index.ts`, `theme/custom.css`) y 17 archivos modificados. Sin frameworks adicionales, sin Vue components.

**Scope:** site/index.md, site/modulos/*.md (×14), site/.vitepress/config.ts, site/.vitepress/theme/ (nuevo).

---

## 1. Paleta de color (Lab Green)

Se sobrescriben las CSS custom properties de VitePress en `site/.vitepress/theme/custom.css`:

| Variable VitePress | Valor nuevo | Uso |
|--------------------|-------------|-----|
| `--vp-c-brand-1` | `#16a34a` | Color de acento principal (links, botones brand) |
| `--vp-c-brand-2` | `#15803d` | Hover y variante oscura |
| `--vp-c-brand-3` | `#4ade80` | Variante clara (backgrounds suaves) |
| `--vp-c-brand-soft` | `#f0fdf4` | Fondo de badges, tips, tarjetas |
| `--vp-home-hero-name-color` | `#14532d` | Texto del nombre del hero |
| `--vp-home-hero-name-background` | `linear-gradient(120deg, #16a34a, #4ade80)` | Gradiente del texto hero |
| `--vp-home-hero-image-background-image` | `radial-gradient(circle, #dcfce7 0%, #f0fdf4 60%)` | Fondo detrás de la imagen del hero |

CSS adicional en `custom.css`:
- `.VPNav`: `border-bottom: 1px solid #dcfce7; background: rgba(240,253,244,0.92); backdrop-filter: blur(8px)`
- `.VPNavBar .title`: `color: #14532d`
- Links activos del sidebar: `color: #16a34a; background: #dcfce7`
- Bloques de código inline: `background: #f0fdf4; color: #15803d`
- Bloques de código fenced: fondo `#0d2818`, texto `#86efac`
- `.custom-block.tip`: border-color `#16a34a`, background `#f0fdf4`

## 2. Theme index

`site/.vitepress/theme/index.ts` extiende el tema por defecto e importa el CSS:

```ts
import DefaultTheme from 'vitepress/theme'
import './custom.css'

export default DefaultTheme
```

## 3. Hero page (site/index.md)

### Cambios en el frontmatter YAML

```yaml
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
```

### Badge de stats sobre el título

Añadir sobre el bloque `hero` en el frontmatter un badge usando la slot `home-hero-info` de VitePress mediante raw HTML en el markdown:

```html
<div class="hero-badge">✓ 142 tests · 0.16s · sin API key</div>
```

CSS en `custom.css`:
```css
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
```

### Features section

Mantener las 6 features existentes. Actualizar el CSS de `.VPFeature` para que coincida con el estilo Lab Green (border `#dcfce7`, background `#f0fdf4`, hover border `#86efac`).

### Quickstart block

Mantener el bloque de código existente. El CSS de bloques fenced lo coloreará automáticamente en verde oscuro.

## 4. Páginas de módulo (site/modulos/NN-nombre.md × 14)

### Estructura nueva de cada página

Cada página pasa de texto plano a un layout con dos columnas usando HTML nativo dentro del Markdown (VitePress lo permite con `<div>`):

```markdown
---
title: "01 — primer-eval"
---

# 01 — primer-eval

<div class="module-layout">
<div class="module-main">

Descripción de una oración.

## Qué aprenderás

- Punto 1
- Punto 2
- Punto 3
- Punto 4

## Código de ejemplo

\`\`\`python
# ejemplo de uso
\`\`\`

## Por qué importa

> Frase de impacto conectando con producción.

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

\`\`\`bash
pytest modules/01-primer-eval/tests/ \
  -m "not slow" -q
\`\`\`

<div class="module-next">
  <div class="next-label">Siguiente →</div>
  <a href="/modulos/02-ragas-basics">02 — ragas-basics</a>
</div>

</div>
</div>
```

### CSS del layout de módulo

```css
.module-layout {
  display: flex;
  gap: 2rem;
  align-items: flex-start;
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
  top: calc(var(--vp-nav-height) + 1rem);
}

.stat-card {
  background: #f0fdf4;
  border: 1px solid #86efac;
  border-radius: 8px;
  padding: 0.6rem;
  text-align: center;
}

.stat-card.stat-ok {
  background: #dcfce7;
}

.stat-number {
  color: #16a34a;
  font-size: 1.4rem;
  font-weight: 900;
  line-height: 1;
}

.stat-number.level {
  font-size: 0.9rem;
  color: #15803d;
}

.stat-label {
  color: #166534;
  font-size: 0.65rem;
  margin-top: 0.15rem;
}

.module-next {
  margin-top: auto;
  padding-top: 0.75rem;
  border-top: 1px solid #dcfce7;
  font-size: 0.8rem;
}

.next-label {
  color: #6b7280;
  font-size: 0.7rem;
  margin-bottom: 0.25rem;
}

.module-next a {
  color: #16a34a;
  font-weight: 600;
  text-decoration: underline;
}

/* Responsive: en móvil, el sidebar va debajo */
@media (max-width: 768px) {
  .module-layout {
    flex-direction: column;
  }
  .module-sidebar {
    width: 100%;
    position: static;
    flex-direction: row;
    flex-wrap: wrap;
  }
  .stat-card {
    flex: 1;
    min-width: 80px;
  }
  .module-next {
    width: 100%;
  }
}
```

### Valores de stats por módulo

Los valores de tests y duración se deben verificar ejecutando antes de escribir cada página:
```bash
pytest modules/NN-nombre/tests/ --collect-only -q 2>/dev/null | tail -1
pytest modules/NN-nombre/tests/ -m "not slow" -q 2>/dev/null | tail -1
```
Los valores de la tabla son una referencia aproximada:



| Módulo | Tests | Duración | API key | Nivel | Siguiente |
|--------|-------|----------|---------|-------|-----------|
| 01-primer-eval | 8 | 0.05s | no | Básico | 02-ragas-basics |
| 02-ragas-basics | 10 | 0.06s | no | Básico | 03-llm-as-judge |
| 03-llm-as-judge | 12 | 0.07s | no | Intermedio | 14-embedding-eval |
| 04-multi-turn | 9 | 0.05s | no | Intermedio | 05-prompt-regression |
| 05-prompt-regression | 11 | 0.06s | no | Intermedio | 06-hallucination-lab |
| 06-hallucination-lab | 10 | 0.06s | no | Intermedio | 07-redteam-garak |
| 07-redteam-garak | 14 | 0.08s | no | Intermedio | 08-redteam-deepteam |
| 08-redteam-deepteam | 12 | 0.07s | no | Intermedio | 09-guardrails |
| 09-guardrails | 11 | 0.06s | no | Avanzado | 10-agent-testing |
| 10-agent-testing | 13 | 0.08s | no | Avanzado | 11-playwright-streaming |
| 11-playwright-streaming | 10 | 0.06s | no | Avanzado | 12-observability |
| 12-observability | 14 | 0.09s | opcional | Avanzado | 13-drift-monitoring |
| 13-drift-monitoring | 15 | 0.09s | no | Avanzado | 14-embedding-eval |
| 14-embedding-eval | 14 | 0.08s | no | Avanzado | — |

## 5. Navegación (site/.vitepress/config.ts)

Cambios menores:
- Añadir `logo: { src: '/logo.svg', width: 24, height: 24 }` — el SVG del logo usa verde `#16a34a`
- El logo SVG es un icono de microscopio simple: `site/public/logo.svg`
- No hay cambios estructurales en sidebar ni nav

## 6. Archivos a crear/modificar

### Nuevos
- `site/.vitepress/theme/index.ts`
- `site/.vitepress/theme/custom.css`
- `site/public/logo.svg` (icono microscopio en verde)

### Modificados
- `site/index.md` — frontmatter + badge HTML
- `site/modulos/01-primer-eval.md` … `site/modulos/14-embedding-eval.md` (×14) — nuevo layout con sidebar
- `site/.vitepress/config.ts` — añadir logo

## 7. Verificación

Tras cada tarea ejecutar:
```bash
cd site && npm run build 2>&1 | tail -5
```

El build debe completarse sin errores ni warnings de links rotos. Tiempo esperado: < 3s.

## 8. Lo que NO entra en este spec

- Modo oscuro (dark mode): VitePress lo soporta pero requiere duplicar todas las variables. Se deja para una iteración futura.
- Componentes Vue custom: descartados explícitamente (Opción C rechazada).
- Animaciones o transiciones CSS complejas.
- Cambios en el contenido textual de las páginas (solo estructura y estilos).
