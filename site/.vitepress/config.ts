import { defineConfig } from "vitepress";

export default defineConfig({
  title: "LLM Testing Lab",
  description:
    "14 módulos pytest para testear LLMs — evaluación RAG, red teaming, guardrails, observabilidad y drift monitoring. Sin API key.",
  lang: "es-ES",

  head: [
    ["link", { rel: "icon", href: "/favicon.svg", type: "image/svg+xml" }],
    ["meta", { property: "og:title", content: "LLM Testing Lab" }],
    [
      "meta",
      {
        property: "og:description",
        content:
          "14 módulos pytest para testear LLMs. 142 tests, 0.16s, sin API key.",
      },
    ],
    ["meta", { property: "og:image", content: "/og.png" }],
    ["meta", { name: "twitter:card", content: "summary_large_image" }],
  ],

  themeConfig: {
    logo: "/logo.svg",
    siteTitle: "LLM Testing Lab",

    nav: [
      { text: "Guía", link: "/guia/" },
      { text: "Módulos", link: "/modulos/" },
      {
        text: "v0.1.0",
        link: "https://github.com/gonzaloMorenoc/ai-testing-lab/releases/tag/v0.1.0",
      },
    ],

    sidebar: {
      "/guia/": [
        {
          text: "Introducción",
          items: [
            { text: "¿Qué es este lab?", link: "/guia/" },
            { text: "Instalación", link: "/guia/instalacion" },
            { text: "Conceptos clave", link: "/guia/conceptos" },
            { text: "Ruta de aprendizaje", link: "/guia/ruta" },
          ],
        },
        {
          text: "Técnicas",
          items: [
            { text: "Métricas de evaluación", link: "/guia/metricas" },
            { text: "Red teaming", link: "/guia/red-teaming" },
            { text: "Observabilidad", link: "/guia/observabilidad" },
          ],
        },
      ],
      "/modulos/": [
        {
          text: "Métricas unitarias",
          items: [
            { text: "01 — primer-eval", link: "/modulos/01-primer-eval" },
            { text: "02 — ragas-basics", link: "/modulos/02-ragas-basics" },
            { text: "03 — llm-as-judge", link: "/modulos/03-llm-as-judge" },
            { text: "14 — embedding-eval", link: "/modulos/14-embedding-eval" },
          ],
        },
        {
          text: "Conversación y regresión",
          items: [
            { text: "04 — multi-turn", link: "/modulos/04-multi-turn" },
            {
              text: "05 — prompt-regression",
              link: "/modulos/05-prompt-regression",
            },
            {
              text: "06 — hallucination-lab",
              link: "/modulos/06-hallucination-lab",
            },
          ],
        },
        {
          text: "Seguridad y safety",
          items: [
            { text: "07 — redteam-garak", link: "/modulos/07-redteam-garak" },
            {
              text: "08 — redteam-deepteam",
              link: "/modulos/08-redteam-deepteam",
            },
            { text: "09 — guardrails", link: "/modulos/09-guardrails" },
          ],
        },
        {
          text: "Producción",
          items: [
            { text: "10 — agent-testing", link: "/modulos/10-agent-testing" },
            {
              text: "11 — playwright-streaming",
              link: "/modulos/11-playwright-streaming",
            },
            { text: "12 — observability", link: "/modulos/12-observability" },
            {
              text: "13 — drift-monitoring",
              link: "/modulos/13-drift-monitoring",
            },
          ],
        },
      ],
    },

    socialLinks: [
      {
        icon: "github",
        link: "https://github.com/gonzaloMorenoc/ai-testing-lab",
      },
    ],

    footer: {
      message: "MIT License",
      copyright: "© 2026 Gonzalo Moreno",
    },

    search: {
      provider: "local",
    },

    editLink: {
      pattern:
        "https://github.com/gonzaloMorenoc/ai-testing-lab/edit/main/site/:path",
      text: "Editar esta página en GitHub",
    },
  },
});
