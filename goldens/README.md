# Goldens

Datasets de evaluación versionados usados por los módulos.

Cada golden dataset tiene formato CSV o JSONL con columnas:
- `input`: pregunta o turno del usuario
- `expected_output`: respuesta de referencia (para métricas reference-based)
- `context`: chunks de contexto recuperados (para métricas RAG)
- `metadata`: JSON con risk_tier, domain, language, golden_version

Los goldens se generan con RAGAS `Synthesizer` o DeepEval `Synthesizer` y se revisan manualmente.
Ver `docs/10-benchmarks-y-datasets.md` para la metodología de creación.
