# Conceptos clave

Glosario de los términos más usados en el laboratorio.

## Evaluación de LLMs

**LLMTestCase** — La unidad básica de evaluación en DeepEval. Encapsula la entrada del usuario, la respuesta del modelo y el contexto recuperado.

**Faithfulness** — ¿La respuesta se puede inferir a partir del contexto recuperado? Una respuesta fiel no añade información que no esté en el contexto.

**Answer Relevancy** — ¿La respuesta responde a lo que se preguntó? Mide si la respuesta está alineada con la pregunta, independientemente de si es correcta.

**Context Precision** — ¿El contexto recuperado es relevante para la pregunta? Mide la calidad del retriever, no del generador.

**Context Recall** — ¿El contexto recuperado contiene toda la información necesaria para responder? Complementario a context precision.

**Groundedness** — ¿Cada afirmación de la respuesta está respaldada por el contexto? Más granular que faithfulness: opera a nivel de claims individuales.

## LLM-as-judge

**G-Eval** — Framework de evaluación donde un LLM puntúa la respuesta siguiendo una rúbrica definida por el usuario. Flexible pero sensible a sesgos.

**Position Bias** — Tendencia del LLM juez a preferir la respuesta que aparece primero cuando compara dos opciones. Se mitiga evaluando en orden inverso y promediando.

**Verbosity Bias** — Tendencia del LLM juez a puntuar mejor las respuestas más largas, independientemente de su calidad.

**DAG Metric** — Métrica definida como un grafo acíclico de condiciones booleanas. Permite lógica compuesta (AND, OR) sin depender de un LLM juez.

## Red teaming

**DAN** (Do Anything Now) — Familia de jailbreaks que intentan convencer al modelo de que "ha sido liberado" de sus restricciones.

**Many-shot jailbreaking** — Técnica que fabrica un historial de conversación ficticio donde el modelo ya aceptó hacer cosas prohibidas, para que continúe en esa dirección.

**Token manipulation** — Insertar guiones, espacios o caracteres unicode entre las letras de una palabra dañina para evadir filtros basados en tokens.

**Indirect injection** — Ocultar instrucciones maliciosas dentro de documentos, páginas web o campos JSON que el modelo procesa como datos.

**Hit rate** — Porcentaje de attack prompts que consiguieron una respuesta comprometida del modelo. Un modelo seguro tiene hit rate cercano a 0.

## Producción y monitorización

**PSI** (Population Stability Index) — Métrica estadística que mide cuánto ha cambiado la distribución de los scores entre un período de referencia y el actual. PSI > 0.2 indica cambio significativo.

**Drift semántico** — Cambio gradual en el significado o la distribución de las respuestas de un modelo a lo largo del tiempo. Puede ocurrir sin cambios en el modelo si cambian los datos de entrada.

**Centroid shift** — Distancia coseno entre el centroide de los embeddings de un corpus de referencia y el corpus actual. Mide el drift semántico a nivel de corpus.

**AlertHistory** — Registro de resultados de una regla de alertas. Permite calcular tendencias: `degrading` (≥2 de los últimos 3 activados), `recovering` (primero activado, últimos 2 limpios), `stable` (exactamente 1 activado).

**Span** — Unidad de trazabilidad en OpenTelemetry. Representa una operación dentro de un pipeline: una llamada LLM, una búsqueda en el retriever, una llamada a herramienta.
