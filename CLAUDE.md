# ai-testing-lab — Instrucciones para Claude

Laboratorio didáctico de testing de LLMs y chatbots. 14 módulos Python independientes,
cada uno con src/, tests/, golden datasets y una página de documentación en VitePress.

## Estructura del proyecto

```
modules/NN-nombre/          ← cada módulo es autocontenido
  conftest.py               ← inserta src/ en sys.path
  src/
    __init__.py
    *.py                    ← implementación (clases, funciones)
  tests/
    conftest.py             ← fixtures compartidas del módulo
    test_*.py               ← tests pytest
    cassettes/              ← cassettes VCR para tests lentos
  README.md
  requirements.md

site/                       ← documentación VitePress (Vercel)
  .vitepress/config.ts
  index.md                  ← hero page
  guia/*.md                 ← guías conceptuales
  modulos/NN-nombre.md      ← página de cada módulo

goldens/NN-nombre/          ← datasets JSONL de referencia
exercises/solutions/        ← soluciones de ejercicios
```

## Convenciones críticas

### Módulos Python
- Cada módulo tiene su propio `conftest.py` raíz que inserta `str(Path(__file__).parent)` en `sys.path`
- Los imports dentro de los tests son `from src.modulo import Clase` (con prefijo `src.`)
- **Excepción módulo 14**: inserta `src/` directamente para evitar colisión de namespace packages
- Los tests NO usan API keys reales — usan mocks, fixtures deterministas o cassettes VCR
- Markers: `@pytest.mark.slow` (llamadas LLM reales), `@pytest.mark.redteam` (nightly), `@pytest.mark.cassette`

### Patrones de código
- Clases inmutables usando dataclasses (`@dataclass(frozen=True)`)
- Funciones < 50 líneas, archivos < 400 líneas
- Type hints en todas las funciones públicas
- Sin comentarios obvios; solo si el WHY no es evidente

### Site VitePress
- Cada nueva página de módulo va en `site/modulos/NN-nombre.md`
- Añadir la entrada en `site/.vitepress/config.ts` bajo la sidebar de Módulos
- El frontmatter mínimo: `---\ntitle: "NN — Nombre"\n---`

## Comandos clave

```bash
# Tests de un módulo
pytest modules/01-primer-eval/tests/ -v -m "not slow"

# Todos los módulos (CI)
pytest modules/ -m "not slow and not redteam" -q

# Linter
ruff check modules/ --fix

# Build del site
cd site && npm run build

# Añadir módulo nuevo completo
# → usar el agente 'module-creator'
```

## Agentes disponibles

| Agente | Cuándo usarlo |
|--------|---------------|
| `module-creator` | Crear un módulo nuevo completo (src + tests + site + ejercicio) |
| `ai-expert` | Preguntas sobre métricas, frameworks de evaluación LLM, diseño de tests |
| `qa-ai-expert` | Diseño de golden datasets, estrategias de regresión, test flakiness |
| `ux-site` | Mejorar navegación, contenido o diseño visual del site VitePress |

## Dependencias

Todas las dependencias están en `pyproject.toml`. Los extras relevantes:
- `ci` — para correr los 14 módulos sin deps pesadas
- `eval` — módulos 01, 02, 06
- `redteam` — módulos 07, 08, 09
- `embeddings` — módulo 14

## Variables de entorno

Ver `.env.example`. Las claves necesarias para tests lentos:
- `OPENAI_API_KEY` — deepeval, ragas
- `LANGFUSE_*` — módulo 12
- `GROQ_API_KEY` — alternativa gratuita

## Flujo de trabajo habitual

1. Crear/modificar código en `modules/NN-nombre/src/`
2. Escribir/actualizar tests en `modules/NN-nombre/tests/`
3. Actualizar `site/modulos/NN-nombre.md` si cambia la API pública
4. `ruff check --fix && pytest modules/NN-nombre/tests/ -v -m "not slow"`
5. Commit con tipo `feat:`, `fix:`, `docs:` o `test:`
