# ¿Qué es este lab?

LLM Testing Lab es un laboratorio práctico de evaluación y testing de sistemas de inteligencia artificial. Está organizado en 14 módulos independientes, cada uno enfocado en una técnica concreta.

## El problema que resuelve

La mayoría de guías sobre calidad en LLMs se quedan en "instala DeepEval" o "usa RAGAS". Esto no es suficiente para entender:

- Por qué una métrica da un score inesperado
- Cómo combinar varias técnicas en un pipeline coherente
- Qué pasa cuando el modelo lleva semanas en producción y nadie se da cuenta de que se está degradando

Este lab muestra cómo funciona cada técnica por dentro, dónde falla, y cuándo usarla.

## Principios de diseño

**Sin llamadas a APIs en los tests rápidos.** Cada módulo corre offline con mocks deterministas. Las llamadas LLM reales están detrás de `@pytest.mark.slow` y usan Groq (free tier). El CI solo ejecuta los tests rápidos.

**Un concepto por módulo.** Cada lab enseña exactamente una técnica de evaluación. Puedes leerlos y ejecutarlos en cualquier orden según lo que necesites.

**Patrones de producción, no juguetes.** AlertHistory, detección de drift con PSI, calibración de position bias, evaluación AST-safe — son patrones que usarías en un sistema real.

**pytest-nativo.** No hay CLIs propias ni frameworks propietarios. Si sabes pytest, ya sabes cómo ejecutar esto.

## Estructura del repositorio

```
ai-testing-lab/
├── modules/          # 14 labs independientes
├── demos/            # sistemas reales sobre los que testear
├── goldens/          # datasets de evaluación versionados
├── docs/             # manual por capítulos + glosario
└── docker/           # Langfuse + Ollama + stack de demos
```

Cada módulo tiene la misma estructura interna:

```
modules/XX-nombre/
├── conftest.py       # sys.path + fixtures compartidos
├── src/              # implementación (el código que se evalúa)
└── tests/            # los tests con pytest
    ├── conftest.py   # fixtures del módulo
    └── test_*.py
```

## Por dónde empezar

Si eres nuevo en evaluación de LLMs → empieza por el [módulo 01](/modulos/01-primer-eval).

Si ya usas RAGAS o DeepEval → ve directamente al módulo que te interese.

Si tienes un sistema en producción y quieres monitorizar → módulos [12](/modulos/12-observability) y [13](/modulos/13-drift-monitoring).

Si te preocupa la seguridad → módulos [07](/modulos/07-redteam-garak), [08](/modulos/08-redteam-deepteam) y [09](/modulos/09-guardrails).
