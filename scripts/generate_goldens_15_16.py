"""Genera golden datasets JSONL para los módulos 15 (cost-aware) y 16 (retrieval-advanced).

Cumple el §9.2 del Manual v13: ≥100 entradas estratificadas por categoría.
Ejecutar desde la raíz del repo:

    python scripts/generate_goldens_15_16.py
"""

from __future__ import annotations

import itertools
import json
import random
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# ---------- Módulo 15: cost-aware-qa ----------

MODELS = [
    ("gpt-4o", "premium", 0.0025, 0.010),
    ("gpt-4o-mini", "small", 0.00015, 0.0006),
    ("claude-sonnet-4-5", "premium", 0.003, 0.015),
    ("claude-haiku-4-5", "small", 0.0008, 0.004),
    ("groq/llama-3.3-70b", "open", 0.00059, 0.00079),
]

QUERY_PROFILES = [
    ("simple_factual", 80, 40, 600, 250),
    ("rag_qa", 1500, 300, 1800, 500),
    ("agent_tool_use", 800, 400, 2400, 700),
    ("creative_writing", 200, 1200, 3200, 400),
    ("structured_extraction", 400, 200, 1100, 350),
]


def _cost(tokens_in: int, tokens_out: int, p_in: float, p_out: float) -> float:
    return round(tokens_in / 1000 * p_in + tokens_out / 1000 * p_out, 6)


def gen_module_15() -> list[dict]:
    rng = random.Random(42)
    rows: list[dict] = []
    for (model, tier, p_in, p_out), (profile, t_in, t_out, lat_p95, ttft) in itertools.product(
        MODELS, QUERY_PROFILES
    ):
        # 4 variaciones por (modelo, perfil) → 5×5×4 = 100
        for v in range(4):
            jitter = 0.8 + (v * 0.15)
            tokens_in = int(t_in * jitter * rng.uniform(0.9, 1.1))
            tokens_out = int(t_out * jitter * rng.uniform(0.9, 1.1))
            latency = round(lat_p95 * jitter * rng.uniform(0.85, 1.15), 1)
            cost = _cost(tokens_in, tokens_out, p_in, p_out)
            tool_calls = rng.randint(0, 3) if profile == "agent_tool_use" else 0
            retried = rng.random() < 0.02
            rows.append(
                {
                    "model": model,
                    "model_tier": tier,
                    "query_profile": profile,
                    "tokens_in": tokens_in,
                    "tokens_out": tokens_out,
                    "latency_ms_total": latency,
                    "time_to_first_token_ms": round(ttft * rng.uniform(0.8, 1.2), 1),
                    "tool_calls": tool_calls,
                    "retried": retried,
                    "cost_usd": cost,
                    "metadata": {
                        "domain": rng.choice(["support", "search", "agent", "summary"]),
                        "risk_tier": rng.choice(["low", "medium", "high"]),
                        "language": rng.choice(["es", "en", "pt"]),
                        "golden_version": "1.0",
                    },
                }
            )
    return rows


# ---------- Módulo 16: retrieval-advanced ----------

DOCS_POOL = {
    # cocina (jerga: nombres de platos, ingredientes)
    "d_cook_01": ("La paella valenciana tradicional lleva arroz bomba, azafrán y conejo.", "cooking"),
    "d_cook_02": ("La fideuá es un plato de fideos similar a la paella pero con marisco.", "cooking"),
    "d_cook_03": ("El gazpacho andaluz es una sopa fría a base de tomate y pimiento.", "cooking"),
    "d_cook_04": ("La tortilla española clásica solo lleva huevo, patata y aceite de oliva.", "cooking"),
    "d_cook_05": ("El cocido madrileño es un guiso de garbanzos con carne y verduras.", "cooking"),
    # tecnología (jerga: siglas, APIs)
    "d_tech_01": ("Python es un lenguaje multipropósito muy usado en data science y backend.", "tech"),
    "d_tech_02": ("Rust ofrece seguridad de memoria sin garbage collector mediante el borrow checker.", "tech"),
    "d_tech_03": ("Kubernetes orquesta contenedores Docker en clusters distribuidos.", "tech"),
    "d_tech_04": ("PostgreSQL soporta JSONB, full-text search y extensiones como PostGIS.", "tech"),
    "d_tech_05": ("GraphQL permite al cliente especificar exactamente los campos de la respuesta.", "tech"),
    # salud
    "d_health_01": ("La hipertensión arterial se diagnostica con valores sostenidos sobre 140/90.", "health"),
    "d_health_02": ("La diabetes tipo 2 se asocia a obesidad y resistencia a la insulina.", "health"),
    "d_health_03": ("El insomnio crónico requiere evaluación médica si dura más de tres meses.", "health"),
    "d_health_04": ("La fibrilación auricular es la arritmia sostenida más común en adultos.", "health"),
    # viajes
    "d_travel_01": ("Lisboa destaca por sus tranvías históricos y el mirador de Santa Catarina.", "travel"),
    "d_travel_02": ("El Camino de Santiago Francés parte desde Saint-Jean-Pied-de-Port.", "travel"),
    "d_travel_03": ("Marrakech es famosa por su zoco, la plaza Jemaa el-Fna y los jardines Majorelle.", "travel"),
    # finanzas
    "d_fin_01": ("Un ETF replica un índice bursátil con costes inferiores a los fondos activos.", "finance"),
    "d_fin_02": ("La inflación reduce el poder adquisitivo si los salarios no se ajustan.", "finance"),
    "d_fin_03": ("Diversificar entre clases de activo reduce la volatilidad de la cartera.", "finance"),
    # ruido
    "d_noise_01": ("Los gatos cazan ratones en jardines por la noche.", "misc"),
    "d_noise_02": ("Las nubes cirros indican buen tiempo a corto plazo.", "misc"),
    "d_noise_03": ("Los volcanes activos en Islandia atraen geólogos cada año.", "misc"),
}

QUERY_SHAPES = [
    "short_ambiguous",
    "conversational",
    "multi_aspect",
    "domain_jargon",
    "position_critical",
    "large_structured_doc",
    "local_context",
    "iterative_reasoning",
]

# 13 queries por shape ⇒ 104 entradas
QUERY_TEMPLATES: dict[str, list[tuple[str, list[str]]]] = {
    "short_ambiguous": [
        ("¿qué es eso?", ["d_cook_01"]),
        ("¿cómo funciona?", ["d_tech_03"]),
        ("dime más", ["d_health_01"]),
        ("explícame", ["d_tech_05"]),
        ("¿y la otra?", ["d_cook_02"]),
        ("¿cuál?", ["d_travel_01"]),
        ("eso mismo", ["d_fin_01"]),
        ("¿el primero?", ["d_health_02"]),
        ("¿qué pasa?", ["d_tech_02"]),
        ("¿por qué?", ["d_cook_03"]),
        ("explica esto", ["d_travel_03"]),
        ("¿qué hay?", ["d_health_04"]),
        ("¿y eso?", ["d_fin_02"]),
    ],
    "conversational": [
        ("oye, ¿qué lleva la paella?", ["d_cook_01"]),
        ("y respecto a la fideuá, ¿qué la diferencia?", ["d_cook_02"]),
        ("hola, ¿python sirve para qué?", ["d_tech_01"]),
        ("mira, cuéntame del rust", ["d_tech_02"]),
        ("vale, ¿y la hipertensión?", ["d_health_01"]),
        ("perfecto, ¿y los ETFs?", ["d_fin_01"]),
        ("pues, ¿cómo es lisboa?", ["d_travel_01"]),
        ("dime, ¿la tortilla española?", ["d_cook_04"]),
        ("oye, ¿el camino de santiago?", ["d_travel_02"]),
        ("vale, ¿qué es la inflación?", ["d_fin_02"]),
        ("entonces, ¿la diabetes tipo 2?", ["d_health_02"]),
        ("eh, ¿kubernetes para qué?", ["d_tech_03"]),
        ("bueno, ¿el insomnio crónico?", ["d_health_03"]),
    ],
    "multi_aspect": [
        ("compara paella y fideuá ingredientes y origen", ["d_cook_01", "d_cook_02"]),
        ("diferencias python rust en seguridad y rendimiento", ["d_tech_01", "d_tech_02"]),
        ("hipertensión diabetes factores de riesgo común", ["d_health_01", "d_health_02"]),
        ("ETFs vs fondos activos coste y diversificación", ["d_fin_01", "d_fin_03"]),
        ("lisboa marrakech transporte y barrios", ["d_travel_01", "d_travel_03"]),
        ("kubernetes graphql cuándo elegir cada uno", ["d_tech_03", "d_tech_05"]),
        ("paella tortilla cocido platos tradicionales españoles", ["d_cook_01", "d_cook_04", "d_cook_05"]),
        ("postgresql graphql cuándo combinarlos", ["d_tech_04", "d_tech_05"]),
        ("insomnio fibrilación pruebas diagnósticas", ["d_health_03", "d_health_04"]),
        ("inflación diversificación protección cartera", ["d_fin_02", "d_fin_03"]),
        ("camino de santiago lisboa transporte público", ["d_travel_01", "d_travel_02"]),
        ("rust python kubernetes stack moderno", ["d_tech_01", "d_tech_02", "d_tech_03"]),
        ("gazpacho fideuá platos fríos y calientes verano", ["d_cook_02", "d_cook_03"]),
    ],
    "domain_jargon": [
        ("JSONB indexación", ["d_tech_04"]),
        ("borrow checker rust", ["d_tech_02"]),
        ("paella bomba azafrán", ["d_cook_01"]),
        ("HBA1c diabetes", ["d_health_02"]),
        ("ratio sharpe diversificación", ["d_fin_03"]),
        ("Jemaa el-Fna zoco", ["d_travel_03"]),
        ("PostGIS geo queries", ["d_tech_04"]),
        ("RLHF DPO alignment", ["d_tech_01"]),
        ("ETF MSCI world", ["d_fin_01"]),
        ("Saint-Jean-Pied-de-Port etapa", ["d_travel_02"]),
        ("garbanzos cocido madrid", ["d_cook_05"]),
        ("fibrilación auricular ECG", ["d_health_04"]),
        ("kubernetes ingress controller", ["d_tech_03"]),
    ],
    "position_critical": [
        ("paella bomba ingredientes exactos", ["d_cook_01"]),
        ("rust borrow checker explicación", ["d_tech_02"]),
        ("kubernetes orquesta contenedores", ["d_tech_03"]),
        ("hipertensión valores 140 90", ["d_health_01"]),
        ("python data science backend", ["d_tech_01"]),
        ("lisboa tranvías mirador", ["d_travel_01"]),
        ("ETF replica indice coste", ["d_fin_01"]),
        ("diabetes tipo 2 obesidad", ["d_health_02"]),
        ("tortilla española solo huevo patata", ["d_cook_04"]),
        ("camino santiago francés origen", ["d_travel_02"]),
        ("inflación poder adquisitivo salarios", ["d_fin_02"]),
        ("postgresql jsonb full text search", ["d_tech_04"]),
        ("marrakech zoco plaza jardines", ["d_travel_03"]),
    ],
    "large_structured_doc": [
        ("capítulo paella receta completa", ["d_cook_01"]),
        ("sección rust seguridad detallada", ["d_tech_02"]),
        ("introducción kubernetes arquitectura", ["d_tech_03"]),
        ("guía hipertensión diagnóstico", ["d_health_01"]),
        ("capítulo ETF inversión pasiva", ["d_fin_01"]),
        ("guía lisboa puntos imperdibles", ["d_travel_01"]),
        ("sección diabetes manejo crónico", ["d_health_02"]),
        ("artículo python aplicaciones", ["d_tech_01"]),
        ("guía marrakech zonas turísticas", ["d_travel_03"]),
        ("sección inflación efectos economía", ["d_fin_02"]),
        ("capítulo cocido recetario madrid", ["d_cook_05"]),
        ("guía camino santiago etapas", ["d_travel_02"]),
        ("capítulo postgresql extensiones", ["d_tech_04"]),
    ],
    "local_context": [
        ("frase paella valenciana", ["d_cook_01"]),
        ("oración rust seguridad", ["d_tech_02"]),
        ("línea kubernetes orquesta", ["d_tech_03"]),
        ("frase hipertensión diagnostico", ["d_health_01"]),
        ("oración ETF replica", ["d_fin_01"]),
        ("frase lisboa tranvías", ["d_travel_01"]),
        ("línea diabetes obesidad", ["d_health_02"]),
        ("oración python data science", ["d_tech_01"]),
        ("frase marrakech zoco", ["d_travel_03"]),
        ("línea inflación poder", ["d_fin_02"]),
        ("frase tortilla huevo patata", ["d_cook_04"]),
        ("oración camino santiago", ["d_travel_02"]),
        ("frase postgresql jsonb", ["d_tech_04"]),
    ],
    "iterative_reasoning": [
        ("primero paella, después fideuá, comparar", ["d_cook_01", "d_cook_02"]),
        ("python para data science, después backend, integración", ["d_tech_01", "d_tech_05"]),
        ("hipertensión diagnóstico, diabetes seguimiento, ambas conjuntas", ["d_health_01", "d_health_02"]),
        ("ETF inicial, diversificar, inflación protección", ["d_fin_01", "d_fin_03", "d_fin_02"]),
        ("lisboa cultura, camino santiago peregrinos, comparar", ["d_travel_01", "d_travel_02"]),
        ("rust empezar, después kubernetes deployment", ["d_tech_02", "d_tech_03"]),
        ("paella aprender, después fideuá variantes", ["d_cook_01", "d_cook_02"]),
        ("postgres jsonb, después graphql query", ["d_tech_04", "d_tech_05"]),
        ("fibrilación detectar, después manejo crónico", ["d_health_04", "d_health_03"]),
        ("marrakech viajar, después lisboa comparativa", ["d_travel_03", "d_travel_01"]),
        ("kubernetes deploy, después postgres backend", ["d_tech_03", "d_tech_04"]),
        ("cocido tradición, después tortilla cotidiana", ["d_cook_05", "d_cook_04"]),
        ("inflación causa, diversificar, ETF protección", ["d_fin_02", "d_fin_03", "d_fin_01"]),
    ],
}


def gen_module_16() -> list[dict]:
    rows: list[dict] = []
    for shape, queries in QUERY_TEMPLATES.items():
        for query, relevant_ids in queries:
            qrels = {doc_id: 2.0 for doc_id in relevant_ids}
            # Añade 1-2 relevantes parciales del mismo dominio
            domain = DOCS_POOL[relevant_ids[0]][1]
            partials = [
                doc_id for doc_id, (_text, dom) in DOCS_POOL.items()
                if dom == domain and doc_id not in relevant_ids
            ][:2]
            for p in partials:
                qrels[p] = 1.0
            rows.append(
                {
                    "query": query,
                    "query_shape": shape,
                    "qrels": qrels,
                    "metadata": {
                        "domain": domain,
                        "n_relevant": len(relevant_ids),
                        "language": "es",
                        "golden_version": "1.0",
                    },
                }
            )
    return rows


# ---------- Documentos compartidos ----------

def gen_corpus_16() -> dict:
    return {
        doc_id: {"text": text, "domain": domain}
        for doc_id, (text, domain) in DOCS_POOL.items()
    }


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    rows15 = gen_module_15()
    rows16 = gen_module_16()
    corpus16 = gen_corpus_16()

    write_jsonl(REPO / "goldens" / "15-cost-aware-qa" / "cost_records.jsonl", rows15)
    write_jsonl(REPO / "goldens" / "16-retrieval-advanced" / "queries.jsonl", rows16)
    write_json(REPO / "goldens" / "16-retrieval-advanced" / "corpus.json", corpus16)

    print(f"Generadas {len(rows15)} entradas en goldens/15-cost-aware-qa/cost_records.jsonl")
    print(f"Generadas {len(rows16)} entradas en goldens/16-retrieval-advanced/queries.jsonl")
    print(f"Corpus de {len(corpus16)} documentos en goldens/16-retrieval-advanced/corpus.json")


if __name__ == "__main__":
    main()
