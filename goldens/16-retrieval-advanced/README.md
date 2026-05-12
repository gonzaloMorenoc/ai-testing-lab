# Golden dataset — 16-retrieval-advanced

104 queries con qrels para evaluar técnicas de retrieval avanzado.

## Estructura

- `queries.jsonl`: 104 queries estratificadas por `query_shape`.
- `corpus.json`: 23 documentos con dominio asociado.

## Estratificación

8 perfiles × 13 queries = 104 entradas:

| Perfil | Técnica recomendada por el manual |
|---|---|
| `short_ambiguous` | HyDE |
| `conversational` | Query rewriting |
| `multi_aspect` | Multi-query retrieval |
| `domain_jargon` | Hybrid search (BM25 + denso) |
| `position_critical` | Reranking |
| `large_structured_doc` | Parent-child chunking |
| `local_context` | Sentence-window |
| `iterative_reasoning` | Self-RAG |

## Esquema

```json
{
  "query": "compara paella y fideuá ingredientes y origen",
  "query_shape": "multi_aspect",
  "qrels": {"d_cook_01": 2.0, "d_cook_02": 2.0, "d_cook_03": 1.0},
  "metadata": {
    "domain": "cooking",
    "n_relevant": 2,
    "language": "es",
    "golden_version": "1.0"
  }
}
```

Los `qrels` siguen la convención TREC: 0 = no relevante, 1 = relevante
parcial, 2 = relevante.

## Dominios cubiertos

- Cocina (5 docs)
- Tecnología (5 docs)
- Salud (4 docs)
- Viajes (3 docs)
- Finanzas (3 docs)
- Ruido / fuera de dominio (3 docs)

## Regeneración

```bash
python scripts/generate_goldens_15_16.py
```

## Política del manual (§9.2)

- Tamaño: 104 entradas ⇒ por encima del mínimo de 100 para gate de release.
- Estratificación: 13 entradas por perfil ⇒ permite reportar `consistency_mean`
  por segmento, no solo media global (Tabla 12.1 antipatrón).
- IAA: pendiente. Los qrels actuales son anotaciones únicas; para gate de
  release exigir IAA ≥ 0.667 (κ de Krippendorff, Cap. 31).
