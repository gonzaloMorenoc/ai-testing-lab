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
|-----------|--------|----------:|-------------|
| `01-primer-eval/qa_golden.jsonl` | 01 | 105 | input, expected_output, context |
| `02-ragas-basics/qa_golden.jsonl` | 02 | 104 | input, expected_output, retrieved_context, umbrales RAGAS |
| `03-llm-as-judge/judge_cases.jsonl` | 03 | 105 | response_a, response_b, expected_winner, known_biases |
| `04-multi-turn/conversations.jsonl` | 04 | 105 | turns, retention_goal, expected_final_response |
| `05-prompt-regression/prompt_versions.jsonl` | 05 | 105 | prompt_id, version, template, expected_output_contains |
| `06-hallucination-lab/claims.jsonl` | 06 | 105 | claims[], grounded, hallucination_present, expected_faithfulness |
| `07-redteam-garak/attack_cases.jsonl` | 07 | 105 | category, prompt, expected_verdict, attack_technique, severity |
| `08-redteam-deepteam/owasp_cases.jsonl` | 08 | 105 | owasp_id, attack_prompt, detection_signals, mitigation |
| `09-guardrails/pii_cases.jsonl` | 09 | 105 | input, expected_pii_types, expected_blocked, language |
| `10-agent-testing/agent_tasks.jsonl` | 10 | 105 | query, expected_tool, expected_trajectory, requires_approval |
| `11-playwright-streaming/playwright_cases.jsonl` | 11 | 105 | action, url, target, assert |
| `12-observability/trace_records.jsonl` | 12 | 105 | trace schema completo (request_id, model, prompt, scores, flags) |
| `13-drift-monitoring/score_distributions.jsonl` | 13 | 105 | scenario, baseline/current/historical scores, expected_drift |
| `14-embedding-eval/retrieval_queries.jsonl` | 14 | 105 | query, relevant_doc_ids, ranked_doc_ids, expected NDCG/MRR/MAP |
| `15-cost-aware-qa/cost_records.jsonl` | 15 | 100 | model, tokens_in/out, latency_ms, cost_usd, retried |
| `16-retrieval-advanced/queries.jsonl` | 16 | 104 | query, query_shape, qrels, domain |

::: tip Política de tamaño
Todos los datasets cumplen el **§9.2 del Manual v13** con ≥ 100 entradas estratificadas. Para regression robusto en alto riesgo, ampliar a 500–1000 con muestras reales de producción. Para gates definitivos, exigir IAA ≥ 0.667 (κ Krippendorff) sobre la anotación.
:::

### Regenerar

```bash
# Goldens de los 14 módulos antiguos
python scripts/expand_old_goldens.py

# Goldens nuevos (módulos 15 y 16)
python scripts/generate_goldens_15_16.py
```

Los scripts usan `random.Random(42)` para reproducibilidad.

## Cómo añadir un golden

1. Añade la línea JSONL al archivo del módulo correspondiente.
2. Incluye siempre `"metadata"` con al menos `domain` y un nivel de dificultad.
3. Abre un PR con la descripción del caso y por qué añade valor al conjunto.

Los goldens se generan con RAGAS `Synthesizer` o DeepEval `Synthesizer` y se revisan manualmente.
Ver `docs/10-benchmarks-y-datasets.md` para la metodología de creación.
