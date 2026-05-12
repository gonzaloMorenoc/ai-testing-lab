---
title: "Marco normativo: EU AI Act, ISO y NIST"
description: "Las normas, reglamentos y framework que un QA AI Engineer tiene que conocer en 2026, y cómo se traducen a tests verificables en el repo."
---

# Marco normativo de QA AI

En QA tradicional el marco regulatorio era opcional. En QA AI ya no. En 2026, la Unión Europea, Estados Unidos, ISO y los reguladores sectoriales (banca, salud, educación) han publicado normas concretas que aplican a cualquier sistema IA en producción. Conocerlas no es responsabilidad de compliance: es responsabilidad de QA aportar la evidencia técnica.

::: tip Aviso editorial
Este manual no es asesoría legal. Los textos oficiales son la única fuente vinculante; las definiciones aquí son operativas para QA. Para decisiones legales, consulta a compliance.
:::

## Los marcos que importan

| Marco | Geografía | Tipo | Qué obliga a QA |
|---|---|---|---|
| **EU AI Act** (Reglamento UE 2024/1689) | UE | Reglamento | Clasificación por riesgo · conformity assessment · monitoring |
| **NIST AI RMF 1.0** | EE.UU. | Voluntario | Funciones Govern / Map / Measure / Manage |
| **ISO/IEC 42001:2023** | Internacional | Norma certificable | Sistema de gestión de IA: control de cambios sobre código + datos + modelos |
| **ISO/IEC 23053:2022** | Internacional | Norma | Marco para sistemas IA basados en ML: calidad de datos, transparencia, tolerancia a fallos |
| **ISO/IEC 23894:2023** | Internacional | Norma | Gestión de riesgo en IA |
| **RGPD / GDPR** | UE | Reglamento | Minimización PII · derecho al olvido · decisiones automatizadas · DPIA |
| **HIPAA, PCI-DSS, FERPA** | EE.UU. sectorial | Reglamentos | PII específica · audit log |
| **MiCA / DORA** | UE finanzas | Reglamentos | Model risk management · tests de resiliencia |

## EU AI Act: categorías de riesgo

El reglamento clasifica los sistemas IA en cuatro categorías. **Solo las dos primeras** requieren acción técnica directa de QA:

| Categoría | Ejemplos | Obligaciones principales |
|---|---|---|
| **Prohibido** | Social scoring, manipulación cognitiva | No se puede desplegar |
| **Alto riesgo** | Triage médico, scoring crediticio, ATS de empleo | Conformity assessment + registro UE + monitoring obligatorio |
| **Riesgo limitado** | Chatbots, generadores de contenido | Declaración explícita de naturaleza IA + watermarking |
| **Riesgo mínimo** | Filtros spam, NPCs | Códigos de conducta voluntarios |

::: warning Sanciones
Las multas alcanzan el **7 % de la facturación global o 35 M EUR** (el mayor) para prácticas prohibidas, y **3 % o 15 M EUR** para alto riesgo. El argumento de negocio para invertir en QA AI riguroso ya es financiero, no solo reputacional.
:::

### Mapeo EU AI Act → tests del repo

| Categoría EU AI Act | Test técnico mínimo | Módulo del repo |
|---|---|---|
| Alto riesgo: triage médico | `faithfulness ≥ 0.90` + revisión humana | `qa_thresholds.RiskLevel.HIGH_RISK` + módulo 06 |
| Alto riesgo: scoring crediticio | Sin bias estadístico entre grupos (Kruskal-Wallis p > 0.01) | módulo 08 |
| Riesgo limitado: chatbot | Declaración + watermarking + faithfulness ≥ 0.85 | módulo 02 (RAGAS) + módulo 04 (multi-turn) |
| Cualquiera: PII | Suite de canary tokens · 0 leaks | módulo 09 |

## ISO/IEC 25010: las 9 características de calidad mapeadas

ISO 25010 es el modelo de calidad de software clásico. La extensión ISO/IEC CT-AI define características específicas para IA. Este manual mapea ambas explícitamente a métricas operativas:

| Característica ISO 25010 | Métrica operativa | Módulo del repo |
|---|---|---|
| Functional suitability | Faithfulness, Answer Relevancy, golden set pass rate | 01, 02, 03 |
| Performance efficiency | P95 latency ≤ 2 s · cost USD/query | 12, 15 |
| Compatibility | OTel trace schema · function calling validation | 10, 12 |
| Interaction capability | Multi-turn coherence · context retention | 04 |
| Reliability | Robustness consistency ≥ 0.80 · drift detection | 07, 13 |
| Security | OWASP LLM Top 10 · prompt injection · PII | 08, 09 |
| Safety | Refusal rate ≥ 0.95 · false refusal rate ≤ 0.05 · toxicity | 09 |
| Maintainability | Prompt regression suite · versionado de prompts | 05 |
| Flexibility | Strategy regression · retrieval avanzado | 05, 16 |

### Características específicas IA (ISTQB CT-AI)

| Característica IA | Métrica operativa | Capítulo manual |
|---|---|---|
| Adaptability | Consistency score bajo perturbaciones (≥ 0.80) | Cap. 12 |
| Autonomy | % acciones que requieren escalado humano | Cap. 21 |
| Evolution | Drift detectado por KS-test (p < 0.01) | Cap. 13 |
| Bias | \|Δ\| entre grupos demográficos (≤ 0.05 con p < 0.01) | Cap. 25 |
| Ethics / Safety | Refusal rate (≥ 0.95) + false refusal rate (≤ 0.05) | Cap. 25 |
| Side effects | Idempotencia y reversibilidad en acciones críticas (100 %) | Cap. 21 |
| Transparency | % requests con trace persistido (100 %) | Cap. 19 |
| Explainability | % respuestas con rationale citado verificable | Cap. 8 |

## Documentación auditable

Tres documentos vivos que un sistema IA maduro produce como parte del ciclo de QA. No son entregables de "una vez": se actualizan en cada release con el changelog.

### Model card

Documento corto (1–3 páginas) que describe **un modelo**. Estructura mínima (Mitchell et al. 2019):

- Propósito del modelo y casos de uso permitidos.
- Datos de entrenamiento (volumen, fechas, fuentes).
- Métricas por subgrupo (idioma, género, edad si aplica).
- Limitaciones conocidas y modos de fallo.
- Casos de uso explícitamente **no** permitidos.

### Datasheet for datasets

Documento que describe **un dataset** (Gebru et al. 2021):

- Origen y motivación.
- Composición y representatividad.
- Recolección y consentimiento.
- Preprocesamiento aplicado.
- Distribución y mantenimiento.

### System card

Análogo al model card pero a nivel de **sistema completo**: model card del LLM + guardrails + monitoring + plan de escalado humano + política de incidentes.

## DPIA: Data Protection Impact Assessment

Requerido por GDPR cuando hay tratamiento automatizado a gran escala o datos sensibles. Lo que QA aporta al DPIA:

| Pregunta del DPIA | Evidencia técnica | Módulo |
|---|---|---|
| ¿Qué PII se procesa? | Inventario + suite de detección PII | 09 |
| ¿Hay riesgo de leakage? | Suite de canary tokens · 0 leaks | 09 |
| ¿Cómo se mide el sesgo? | Kruskal-Wallis por grupo demográfico | 08 |
| ¿Qué se loguea y por cuánto tiempo? | Trace schema + política de retención | 12 |
| ¿Hay rollback automático? | Gates de canary deployment | 18 (CI/CD) |

## Shadow AI: el riesgo organizacional

Los empleados que pegan código en ChatGPT personal o suben datos a Claude.ai sin aprobación formal son el equivalente del **shadow IT** de hace una década. ISTQB CT-GenAI §5.1.1 lo identifica como uno de los riesgos de mayor crecimiento.

Riesgos:
- Privacidad y seguridad de datos: las herramientas personales no tienen los controles del enterprise tier.
- Cumplimiento: violación de RGPD o normativas sectoriales.
- Propiedad intelectual: acuerdos de licencia poco claros.
- Calidad inconsistente: cada equipo usa modelos y prompts distintos, sin métricas comparables.

Mitigación:
- Política clara de IA aprobada (lista positiva de modelos y herramientas).
- Provisión interna empresarial (Azure OpenAI, Bedrock, Vertex AI).
- Formación: qué datos no pueden enviarse a un LLM público.
- Observabilidad organizacional: inventario de usos de IA.

## Checklist mínimo de compliance para QA AI

Antes de aprobar un release en dominio regulado, verificar:

- [ ] Clasificación de riesgo según EU AI Act documentada.
- [ ] Características ISO 25010 e ISTQB mapeadas a métricas operativas.
- [ ] Model card y system card actualizados con el release.
- [ ] DPIA completada si aplica (PII a gran escala).
- [ ] Política de shadow AI publicada y aplicada en la organización.
- [ ] Plan de adopción organizacional alineado con la fase actual del equipo.
- [ ] Gates de la [Tabla 4.2](./umbrales) en CI/CD, con `RiskLevel.HIGH_RISK` para dominios regulados.

::: tip La división del trabajo
QA AI **no** es responsable del cumplimiento normativo en exclusiva: se comparte con compliance, legal y security. QA aporta la **evidencia técnica** (métricas, trazas, datasets versionados, model cards). Sin esa evidencia, el resto del programa de cumplimiento queda sin soporte.
:::

## Referencias

- EU AI Act — [digital-strategy.ec.europa.eu/policies/ai-act](https://digital-strategy.ec.europa.eu/policies/ai-act)
- NIST AI RMF 1.0 — [nist.gov/itl/ai-risk-management-framework](https://www.nist.gov/itl/ai-risk-management-framework)
- ISO/IEC 42001:2023 — AI Management Systems
- ISO/IEC 23053:2022 — Framework for AI Systems Using ML
- Mitchell et al. (2019) — Model Cards for Model Reporting
- Gebru et al. (2021) — Datasheets for Datasets
- Manual QA AI v13 — Cap. 3 (Riesgos, calidad y marco normativo)
