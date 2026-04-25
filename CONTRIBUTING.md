# Cómo contribuir

Gracias por querer mejorar el laboratorio. Aquí tienes todo lo que necesitas saber.

## Tipos de contribución

### Reportar un problema con una métrica
Si los scores de un evaluador no correlacionan con tu juicio humano, abre un issue describiendo:
- Módulo afectado
- Input que usaste (query, context, response)
- Score que devolvió el evaluador
- Por qué crees que es incorrecto

### Añadir un caso golden
Los datasets de evaluación viven en `goldens/`. Cada fichero es un JSONL donde cada línea es un caso con `input`, `context`, `expected_output` y opcionalmente `metadata`.

Sigue el formato de `goldens/README.md`, añade tu caso al fichero correspondiente y abre un PR.

### Proponer un módulo nuevo
Abre un issue con:
- El concepto que enseñaría (una frase)
- El módulo más cercano como referencia
- Una idea de qué tests tendría

No hace falta implementarlo para proponer. La discusión en el issue sirve para alinearse antes de escribir código.

### Corregir el manual
Los capítulos viven en `docs/`. Errores factuales, links rotos o ejemplos que ya no funcionan — PR directo, sin necesidad de issue previo.

### Mejorar un módulo existente
Revisa los issues abiertos con la etiqueta `enhancement`. Si quieres implementar algo que no está listado, abre un issue antes de empezar para evitar trabajo duplicado.

---

## Cómo empezar

```bash
git clone https://github.com/gonzaloMorenoc/ai-testing-lab.git
cd ai-testing-lab
pip install -e ".[dev]"        # instala ruff, mypy, pytest, pytest-cov
pre-commit install             # activa los hooks de lint automático
```

Verifica que los tests pasan antes de tocar nada:

```bash
pytest modules/ -m "not slow and not redteam" -q
# debe terminar con: 142 passed in ~0.2s
```

---

## Flujo de trabajo

1. Crea una rama desde `main`: `git checkout -b mi-mejora`
2. Escribe el test primero (ver más abajo)
3. Implementa el mínimo código para que pase
4. Comprueba que el linter no se queja: `ruff check .`
5. Abre un PR describiendo qué cambió y por qué

---

## Tests

Todos los tests rápidos deben pasar **sin API key ni conexión a internet**. Si tu contribución requiere una llamada LLM real, márcala con `@pytest.mark.slow` y añade una guarda:

```python
@pytest.mark.slow
def test_con_llamada_real() -> None:
    if not os.getenv("GROQ_API_KEY"):
        pytest.skip("GROQ_API_KEY no encontrado")
    ...
```

Cada módulo tiene su `conftest.py` con los fixtures compartidos. Úsalos en lugar de crear datos ad-hoc en cada test.

---

## Estilo de código

El proyecto usa `ruff` para lint y formato. La configuración está en `pyproject.toml`. Antes de hacer push:

```bash
ruff check . --fix
ruff format .
```

Los hooks de pre-commit lo hacen automáticamente si has ejecutado `pre-commit install`.

---

## Convención de commits

```
<tipo>: <descripción en imperativo>
```

Tipos habituales: `feat`, `fix`, `test`, `docs`, `refactor`, `ci`

Ejemplos:
```
feat: añadir detección de sesgo de longitud en módulo 03
fix: corregir cálculo de PSI cuando un bin tiene frecuencia cero
test: añadir caso de negación compuesta en hallucination-lab
docs: actualizar glosario con definición de centroid shift
```

---

## Preguntas

Abre un issue con la etiqueta `question`. No hay preguntas tontas si estás intentando aprender.
