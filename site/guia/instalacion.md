# Instalación

## Requisitos

- Python 3.11 o 3.12
- pip o uv

## Instalación mínima

Para ejecutar los tests rápidos de cualquier módulo sin API key:

```bash
git clone https://github.com/gonzaloMorenoc/ai-testing-lab.git
cd ai-testing-lab
pip install deepeval pytest pytest-cov numpy
```

## Verificar que funciona

```bash
pytest modules/01-primer-eval/tests/ -m "not slow" -q
```

Resultado esperado:

```
........ 8 passed in 0.12s
```

## Ejecutar la suite completa

```bash
pytest modules/ -m "not slow and not redteam" -q
```

```
142 passed, 1 skipped in 0.16s
```

## Tests con llamadas LLM reales

Los tests marcados con `@pytest.mark.slow` usan un modelo real. Se recomienda Groq (free tier):

```bash
export GROQ_API_KEY=tu_clave_aqui
pytest modules/ -m "slow" -q
```

Consigue tu API key gratuita en [console.groq.com](https://console.groq.com).

## Dev Container

Si usas VS Code, el repositorio incluye un Dev Container preconfigurado. Haz clic en el badge del README o abre la paleta de comandos y selecciona **Dev Containers: Reopen in Container**.

Incluye Python 3.12, todas las dependencias de desarrollo y los hooks de pre-commit ya instalados.

## Instalación completa (desarrollo)

Para contribuir al proyecto o ejecutar el linter:

```bash
pip install -e ".[dev]"
pre-commit install
```

Esto instala `ruff`, `mypy`, `pytest` y configura los hooks automáticos de lint y formato.
