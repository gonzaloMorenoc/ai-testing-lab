# Testing de chatbots conversacionales clásicos

> Parte del [Manual de Testing de Chatbots y LLMs](./manual-completo.md).

---

## 8. Testing de chatbots conversacionales clásicos

### 8.1 Botium – "el Selenium de los chatbots"
Open source, con 55+ connectors: Dialogflow, Rasa, Amazon Lex, IBM Watson, Microsoft Bot Framework, web widgets (Selenium-based), REST/gRPC, voz ([botium-docs.readthedocs.io](https://botium-docs.readthedocs.io/), [github.com/codeforequity-at/botium-core](https://github.com/codeforequity-at/botium-core)). Usa **BotiumScript**, un DSL simple:
```
#me
hello bot!
#bot
Hello, humanoid! How can I help you ?
```
Soporta `convo files` (flujo esperado) + `utterances files` (N formas de decir lo mismo) para cubrir la variabilidad en el lenguaje del usuario. **Botium Crawler** auto-descubre flujos haciendo clicks en quick replies y genera tests de regresión. Botium Speech Processing permite probar IVRs voice-first. Ecosistema: **Botium Core**, **CLI**, **Box** (UI enterprise), **Bindings** (integra con Jasmine/Mocha/Jest), **Coach** (métricas NLP continuas).

### 8.2 Rasa Pro test framework
Tres niveles ([rasa.com](https://rasa.com/docs/rasa-pro/nlu-based-assistants/testing-your-assistant/)):
- `rasa data validate` – chequea inconsistencias antes de entrenar.
- `rasa test nlu` – cross-validation de intents/entities, genera confusion matrix + histogramas de confianza ([legacy-docs-oss.rasa.com](https://legacy-docs-oss.rasa.com/docs/rasa/reference/rasa/nlu/test/)).
- `rasa test e2e` – stories YAML con asserts sobre slots, flows, custom actions y `generative_response_is_relevant`.

### 8.3 Otras stacks
- **Dialogflow CX** – test cases propios en consola + API; intégralos en CI con el Python client.
- **Microsoft Bot Framework** – Bot Framework Emulator + `botbuilder-testing` para unit tests.
- **IBM Watson Assistant** – dialog tests nativos + Botium connector.
- **Cyara / Cognigy** – enterprise voice/IVR; Cyara simula miles de llamadas concurrentes, validación end-to-end de SIP + STT + NLU.

### 8.4 BDD para chatbots
Con Robot Framework (que ya usas) o `behave`/`pytest-bdd`, puedes escribir:
```gherkin
Scenario: Usuario consulta devolución
  Given El usuario abre el chat
  When Envía "¿política de devoluciones?"
  Then La respuesta debe contener "30 días"
  And La respuesta debe estar fundamentada en la base de conocimiento
```
Luego el step llama al bot (Botium o API directa) y las aserciones corren métricas DeepEval/RAGAS.

---

## Laboratorios relacionados

| Módulo | Descripción |
|--------|-------------|
| [04-multi-turn](../modules/04-multi-turn/) | Testing de conversaciones multi-turno |
| [11-playwright-streaming](../modules/11-playwright-streaming/) | Playwright contra UIs de chatbot |
| [demos/rasa-intent-bot](../demos/rasa-intent-bot/) | Demo Rasa OSS para practicar NLU testing |
