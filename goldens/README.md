# Goldens

Datasets de evaluación versionados usados por los módulos.

## Formato

Cada archivo JSONL contiene un registro por línea con los campos relevantes al tipo de módulo:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `input` | string | Pregunta o turno del usuario |
| `expected_output` | string | Respuesta de referencia (métricas reference-based) |
| `context` / `retrieved_context` | list[string] | Chunks recuperados (métricas RAG) |
| `metadata` | object | `domain`, `difficulty`, umbrales mínimos de métrica |

## Datasets disponibles

| Directorio | Módulo | Registros | Campos clave |
|-----------|--------|-----------|-------------|
| `01-primer-eval/qa_golden.jsonl` | 01 | 15 | input, expected_output, context |
| `02-ragas-basics/qa_golden.jsonl` | 02 | 10 | input, expected_output, retrieved_context, umbrales RAGAS |
| `03-llm-as-judge/judge_cases.jsonl` | 03 | 11 | response_a, response_b, expected_winner, known_biases |
| `04-multi-turn/conversations.jsonl` | 04 | 10 | turns, retention_goal, expected_final_response_contains |
| `05-prompt-regression/prompt_versions.jsonl` | 05 | 11 | prompt_id, version, template, expected_output_contains |
| `06-hallucination-lab/claims.jsonl` | 06 | 9 | claims[], grounded, hallucination_type, expected_faithfulness |

## Cómo añadir un golden

1. Añade la línea JSONL al archivo del módulo correspondiente.
2. Incluye siempre `"metadata"` con al menos `domain` y un nivel de dificultad.
3. Abre un PR con la descripción del caso y por qué añade valor al conjunto.

Los goldens se generan con RAGAS `Synthesizer` o DeepEval `Synthesizer` y se revisan manualmente.
Ver `docs/10-benchmarks-y-datasets.md` para la metodología de creación.
