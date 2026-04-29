# Métricas de evaluación

Resumen de todas las métricas usadas en el laboratorio, con sus rangos, fortalezas y cuándo usarlas.

## Métricas de RAG

| Métrica | Rango | Qué mide | Módulo |
|---------|:-----:|----------|--------|
| Faithfulness | 0–1 | ¿La respuesta se infiere del contexto? | 01, 02 |
| Answer Relevancy | 0–1 | ¿La respuesta responde a la pregunta? | 01, 02 |
| Context Precision | 0–1 | ¿El contexto recuperado es relevante? | 02 |
| Context Recall | 0–1 | ¿El contexto contiene todo lo necesario? | 02 |
| Groundedness | 0–1 | ¿Cada claim está en el contexto? | 06 |

## Métricas de juez LLM

| Métrica | Rango | Qué mide | Módulo |
|---------|:-----:|----------|--------|
| G-Eval | 0–1 | Puntuación según rúbrica personalizada | 03 |
| DAG Metric | True/False | Condiciones booleanas compuestas | 03 |
| Position Bias Delta | 0–1 | Diferencia de score según posición | 03 |

## Métricas de seguridad

| Métrica | Rango | Qué mide | Módulo |
|---------|:-----:|----------|--------|
| Hit Rate | 0–1 | % de ataques que tuvieron éxito | 07, 08 |
| Hit Rate by Category | 0–1 | Hit rate desglosado por tipo de ataque | 07 |

## Métricas de drift

| Métrica | Rango | Qué mide | Módulo |
|---------|:-----:|----------|--------|
| PSI | 0–∞ | Cambio en distribución de scores | 13 |
| Mean Drop | % | Caída del score medio respecto al baseline | 13 |
| P95 | 0–1 | Percentil 95 de los scores actuales | 13 |
| Centroid Shift | 0–1 | Distancia coseno entre centroides de embeddings | 14 |
| Cosine Similarity | -1–1 | Similitud semántica entre dos textos | 14 |

## Cuándo usar cada una

**Para evaluar una respuesta individual:**
→ Faithfulness + Answer Relevancy (módulo 01)

**Para evaluar un pipeline RAG completo:**
→ Faithfulness + Context Precision + Context Recall (módulo 02)

**Para comparar dos versiones de un prompt:**
→ G-Eval con calibración de position bias (módulo 03) + is_significant() (módulo 05)

**Para detectar alucinaciones:**
→ Groundedness con detección de negaciones (módulo 06)

**Para monitorizar calidad en producción:**
→ PSI + Mean Drop + Centroid Shift (módulos 13 + 14)
