# Graph Report - .  (2026-09-07)

## Corpus Check
- 7 files · ~9,231 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 173 nodes · 299 edges · 19 communities (14 shown, 5 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 29 edges (avg confidence: 0.6)
- Token cost: 65,000 input · 4,700 output

## Community Hubs (Navigation)
- Componente B y tests de resiliencia
- Entregable A: orquestador concurrente
- Fase 2 Componente C: pipeline validado (codigo)
- Entregable B: modulos y contrato base
- GeminiClient y ChatMessage (streaming)
- Documentacion Fase 2: LangChain y pipeline
- AsyncLLMManager (Factory) y LLMConfig
- GroqClient y ModelResponse
- Panorama del curso (Modulos 2-8)
- Spec Entregable B y proveedores (Fase 1)
- Script de validacion main.py (Fase 1)
- Fase 2 Componente A: refactorizacion LCEL
- OpenAIClient (Fase 1)
- conftest.py (setup de tests)
- Spec Componente A (Fase 2)
- Decision: reemplazo de AsyncLLMManager por LangChain
- Import BaseModel (ejercicio B)

## God Nodes (most connected - your core abstractions)
1. `ChatMessage` - 25 edges
2. `ModelResponse` - 18 edges
3. `BaseLLMClient` - 16 edges
4. `AsyncLLMManager` - 14 edges
5. `GeminiClient` - 12 edges
6. `Provider` - 12 edges
7. `GroqClient` - 11 edges
8. `OpenAIClient` - 11 edges
9. `process_text()` - 11 edges
10. `orquestar_tres_modelos()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `asyncio.timeout (seguro contra latencia infinita)` --conceptually_related_to--> `orquestar_tres_modelos()`  [INFERRED]
  program-summary.pdf → entregable_a_orquestador/orquestador_concurrente.py
- `asyncio.Semaphore (control de flujo y rate limits)` --conceptually_related_to--> `orquestar_con_semaforo()`  [INFERRED]
  program-summary.pdf → entregable_a_orquestador/orquestador_concurrente.py
- `Ejercicio: Orquestador Concurrente de Modelos (practica Modulo 1)` --conceptually_related_to--> `orquestar_tres_modelos()`  [INFERRED]
  program-summary.pdf → entregable_a_orquestador/orquestador_concurrente.py
- `Modulo 1: La interfaz base - conexion y abstraccion de LLMs` --conceptually_related_to--> `Programa AI Engineering (8 fases)`  [INFERRED]
  program-summary.pdf → contexto_fase1.md
- `Ejercicio: Orquestador Concurrente de Modelos (practica Modulo 1)` --conceptually_related_to--> `Especificacion Entregable A: Orquestador Concurrente de Modelos`  [INFERRED]
  program-summary.pdf → contexto_fase1.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Synthetic Resilience Testing via Dependency Injection** — tests_test_fase2_resilience, fase2_pipeline_validado_readme_process_text, fase2_pipeline_validado_readme_run_validated_chain, fase2_pipeline_validado_readme_resilient_model_injection, fase2_pipeline_validado_readme_runnable_falso [INFERRED 0.85]
- **Fase 2 — Tres componentes evaluables del curso AI Engineering** — contexto_fase2_componente_a, contexto_fase2_componente_b, contexto_fase2_componente_c [EXTRACTED 1.00]
- **Demo 1: gather + timeout sobre tres llamadas simuladas a modelos** — entregable_a_orquestador_orquestador_concurrente_orquestar_tres_modelos, entregable_a_orquestador_orquestador_concurrente_gpt_4_call, entregable_a_orquestador_orquestador_concurrente_claude_3_call, entregable_a_orquestador_orquestador_concurrente_local_llama_call [INFERRED 0.85]
- **Proveedores de IA gratuitos recomendados para Entregable B** — contexto_fase1_provider_gemini, contexto_fase1_provider_groq, contexto_fase1_provider_ollama [INFERRED 0.75]

## Communities (19 total, 5 thin omitted)

### Community 0 - "Componente B y tests de resiliencia"
Cohesion: 0.11
Nodes (27): EntityExtraction, Runnable, Componente B - Fase 2: Validacion estructurada y resiliencia en cadenas.…, Contrato de datos validado que debe devolver el LLM., Extrae entidades del texto de forma validada y resiliente ante fallos.…, run_validated_chain(), Inyeccion de modelo resiliente (resilient_model / resilient_llm), run_validated_chain() (+19 more)

### Community 1 - "Entregable A: orquestador concurrente"
Cohesion: 0.11
Nodes (27): Programa AI Engineering (8 fases), Especificacion Entregable A: Orquestador Concurrente de Modelos, Evidencia de ejecucion (logs de consola Demo 1 y Demo 2), claude_3_call(), gpt_4_call(), llamada_simulada(), local_llama_call(), main() (+19 more)

### Community 2 - "Fase 2 Componente C: pipeline validado (codigo)"
Cohesion: 0.13
Nodes (16): build_chain(), process_text(), Runnable, Cadena LCEL del Pipeline de Extraccion de Entidades Tecnicas. prompt |…, Compone prompt | model.with_structured_output(TechExtraction) + retry.…, Procesa un parrafo de texto y devuelve un TechExtraction validado. Nunca deja…, main(), Mini-script de prueba del Pipeline de Extraccion de Entidades Tecnicas. Ejecuta… (+8 more)

### Community 3 - "Entregable B: modulos y contrato base"
Cohesion: 0.22
Nodes (12): ABC, BaseLLMClient, Abstract contract that every provider-specific LLM client must implement., Contrato que todo cliente de LLM debe cumplir, sin importar el proveedor real…, Google Gemini provider client (free tier, no credit card required)., Groq provider client (free tier, no credit card required). Groq expone una API…, AsyncLLMManager: punto de entrada unico y agnostico al proveedor (patron…, OpenAI provider client. Nota: OpenAI no tiene free tier (requiere tarjeta y… (+4 more)

### Community 4 - "GeminiClient y ChatMessage (streaming)"
Cohesion: 0.22
Nodes (7): Content, Genera la respuesta token a token (modo streaming)., GeminiClient, Gemini separa el system prompt del resto y llama 'model' al rol del asistente., ChatMessage, A single message in a conversation., field_validator

### Community 5 - "Documentacion Fase 2: LangChain y pipeline"
Cohesion: 0.21
Nodes (12): Componente B — Validacion estructurada y resiliencia en cadenas (consigna), Componente C — Pipeline de procesamiento validado (Pre-entrega 2, consigna), EntityExtraction (Pydantic schema, ejercicio TODO), Rationale: preferir proveedores gratuitos (Groq/Gemini) con soporte with_structured_output, with_retry(), with_structured_output(), chain.py, main.py (+4 more)

### Community 6 - "AsyncLLMManager (Factory) y LLMConfig"
Cohesion: 0.28
Nodes (5): BaseModel, AsyncLLMManager, Recibe un LLMConfig, arma internamente el cliente concreto y delega en el., LLMConfig, Configuration required to instantiate a provider client via the factory.

### Community 7 - "GroqClient y ModelResponse"
Cohesion: 0.29
Nodes (4): Genera una respuesta completa (modo normal, no streaming)., GroqClient, ModelResponse, Uniform response returned by every client, success or failure.

### Community 8 - "Panorama del curso (Modulos 2-8)"
Cohesion: 0.25
Nodes (8): Curso AI Engineering (Coderhouse, 8 modulos, 30 horas), Modulo 2: Encadenamiento logico - orquestacion con LangChain (LCEL), Modulo 3: Persistencia de datos y vector DBs, Modulo 4: Escalabilidad documental - RAG avanzado y Pinecone, Modulo 5: Razonamiento autonomo - agentes con LangGraph, Modulo 6: Sistemas multi-agente - colaboracion y especializacion, Modulo 7: Produccion y robustez - observabilidad, costos y despliegue, Modulo 8: Capstone - entrega final

### Community 9 - "Spec Entregable B y proveedores (Fase 1)"
Cohesion: 0.29
Nodes (7): Especificacion Entregable B: Cliente de LLM robusto y asincrono, Anthropic (proveedor de pago), Google Gemini (proveedor gratuito recomendado), Groq (proveedor gratuito recomendado), Ollama local (proveedor gratuito recomendado), OpenAI (proveedor de pago), Notebook de referencia: Pista_Pre_entrega_1_Cliente_de_LLM_robusto_y_asincrono.ipynb

### Community 10 - "Script de validacion main.py (Fase 1)"
Cohesion: 0.60
Nodes (4): main(), probar_proveedor(), Script de validacion del Unified Async LLM Client. Carga las variables de…, LLMConfig

### Community 11 - "Fase 2 Componente A: refactorizacion LCEL"
Cohesion: 0.50
Nodes (4): build_chain(), main(), Componente A - Fase 2: Refactorizacion a LCEL Asincrono. Reemplaza la llamada…, Compone prompt | model | parser usando el operador LCEL.

## Knowledge Gaps
- **16 isolated node(s):** `Google Gemini (proveedor gratuito recomendado)`, `Groq (proveedor gratuito recomendado)`, `Ollama local (proveedor gratuito recomendado)`, `OpenAI (proveedor de pago)`, `Anthropic (proveedor de pago)` (+11 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `EntityExtraction` connect `Componente B y tests de resiliencia` to `AsyncLLMManager (Factory) y LLMConfig`?**
  _High betweenness centrality (0.141) - this node is a cross-community bridge._
- **Why does `ChatMessage` connect `GeminiClient y ChatMessage (streaming)` to `Entregable B: modulos y contrato base`, `OpenAIClient (Fase 1)`, `AsyncLLMManager (Factory) y LLMConfig`, `GroqClient y ModelResponse`?**
  _High betweenness centrality (0.121) - this node is a cross-community bridge._
- **Why does `ModelResponse` connect `GroqClient y ModelResponse` to `Entregable B: modulos y contrato base`, `GeminiClient y ChatMessage (streaming)`, `OpenAIClient (Fase 1)`, `AsyncLLMManager (Factory) y LLMConfig`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `ChatMessage` (e.g. with `BaseLLMClient` and `GeminiClient`) actually correct?**
  _`ChatMessage` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `ModelResponse` (e.g. with `BaseLLMClient` and `GeminiClient`) actually correct?**
  _`ModelResponse` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `BaseLLMClient` (e.g. with `ChatMessage` and `ModelResponse`) actually correct?**
  _`BaseLLMClient` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `AsyncLLMManager` (e.g. with `BaseLLMClient` and `GeminiClient`) actually correct?**
  _`AsyncLLMManager` has 8 INFERRED edges - model-reasoned connections that need verification._