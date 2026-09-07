# Graph Report - .  (2026-09-07)

## Corpus Check
- 11 files · ~8,296 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 161 nodes · 271 edges · 16 communities (13 shown, 3 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 31 edges (avg confidence: 0.61)
- Token cost: 70,000 input · 4,000 output

## Community Hubs (Navigation)
- Documentacion Fase 2: LangChain y LCEL
- Panorama del curso y spec de Fase 1
- Entregable A: orquestador concurrente
- Fase 2 Componente C: pipeline validado (codigo)
- Entregable B: modulos y contrato base
- AsyncLLMManager (Factory) y OpenAIClient
- Clientes concretos: streaming y ChatMessage
- GroqClient y ModelResponse
- Fase 2 Componente B: validacion estructurada
- Script de validacion main.py (Fase 1)
- Fase 2 Componente A: refactorizacion LCEL
- Dependencia google-genai
- Dependencia openai
- Dependencia python-dotenv

## God Nodes (most connected - your core abstractions)
1. `ChatMessage` - 25 edges
2. `ModelResponse` - 18 edges
3. `BaseLLMClient` - 16 edges
4. `AsyncLLMManager` - 14 edges
5. `GeminiClient` - 12 edges
6. `Provider` - 12 edges
7. `GroqClient` - 11 edges
8. `OpenAIClient` - 11 edges
9. `orquestar_tres_modelos()` - 10 edges
10. `Curso AI Engineering (Coderhouse, 8 modulos, 30 horas)` - 8 edges

## Surprising Connections (you probably didn't know these)
- `asyncio.timeout (seguro contra latencia infinita)` --conceptually_related_to--> `orquestar_tres_modelos()`  [INFERRED]
  program-summary.pdf → entregable_a_orquestador/orquestador_concurrente.py
- `Ejercicio: Orquestador Concurrente de Modelos (practica Modulo 1)` --conceptually_related_to--> `orquestar_tres_modelos()`  [INFERRED]
  program-summary.pdf → entregable_a_orquestador/orquestador_concurrente.py
- `asyncio.Semaphore (control de flujo y rate limits)` --conceptually_related_to--> `orquestar_con_semaforo()`  [INFERRED]
  program-summary.pdf → entregable_a_orquestador/orquestador_concurrente.py
- `Modulo 1: La interfaz base - conexion y abstraccion de LLMs` --conceptually_related_to--> `Programa AI Engineering (8 fases)`  [INFERRED]
  program-summary.pdf → contexto_fase1.md
- `Ejercicio: Orquestador Concurrente de Modelos (practica Modulo 1)` --conceptually_related_to--> `Especificacion Entregable A: Orquestador Concurrente de Modelos`  [INFERRED]
  program-summary.pdf → contexto_fase1.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Fase 2 — Tres componentes evaluables del curso AI Engineering** — contexto_fase2_componente_a, contexto_fase2_componente_b, contexto_fase2_componente_c [EXTRACTED 1.00]
- **Modelos Pydantic de validacion (Fase 1 y Fase 2)** — contexto_fase2_entityextraction, fase2_pipeline_validado_readme_techextraction [INFERRED 0.85]
- **Demo 1: gather + timeout sobre tres llamadas simuladas a modelos** — entregable_a_orquestador_orquestador_concurrente_orquestar_tres_modelos, entregable_a_orquestador_orquestador_concurrente_gpt_4_call, entregable_a_orquestador_orquestador_concurrente_claude_3_call, entregable_a_orquestador_orquestador_concurrente_local_llama_call [INFERRED 0.85]
- **Proveedores de IA gratuitos recomendados para Entregable B** — contexto_fase1_provider_gemini, contexto_fase1_provider_groq, contexto_fase1_provider_ollama [INFERRED 0.75]

## Communities (16 total, 3 thin omitted)

### Community 0 - "Documentacion Fase 2: LangChain y LCEL"
Cohesion: 0.11
Nodes (27): Componente A — Refactorizacion a LCEL Asincrono (consigna), Componente B — Validacion estructurada y resiliencia en cadenas (consigna), Componente C — Pipeline de procesamiento validado (Pre-entrega 2, consigna), EntityExtraction (Pydantic schema, ejercicio TODO), Rationale: preferir proveedores gratuitos (Groq/Gemini) con soporte with_structured_output, Rationale: reemplazar AsyncLLMManager propio por LangChain/LCEL, with_retry(), with_structured_output() (+19 more)

### Community 1 - "Panorama del curso y spec de Fase 1"
Cohesion: 0.09
Nodes (23): Programa AI Engineering (8 fases), Especificacion Entregable A: Orquestador Concurrente de Modelos, Especificacion Entregable B: Cliente de LLM robusto y asincrono, Anthropic (proveedor de pago), Google Gemini (proveedor gratuito recomendado), Groq (proveedor gratuito recomendado), Ollama local (proveedor gratuito recomendado), OpenAI (proveedor de pago) (+15 more)

### Community 2 - "Entregable A: orquestador concurrente"
Cohesion: 0.17
Nodes (19): Evidencia de ejecucion (logs de consola Demo 1 y Demo 2), claude_3_call(), gpt_4_call(), llamada_simulada(), local_llama_call(), main(), orquestar_con_semaforo(), orquestar_tres_modelos() (+11 more)

### Community 3 - "Fase 2 Componente C: pipeline validado (codigo)"
Cohesion: 0.15
Nodes (15): Enum, build_chain(), process_text(), Cadena LCEL del Pipeline de Extraccion de Entidades Tecnicas. prompt |…, Compone prompt | model.with_structured_output(TechExtraction) + retry., Procesa un parrafo de texto y devuelve un TechExtraction validado. Nunca deja…, main(), Mini-script de prueba del Pipeline de Extraccion de Entidades Tecnicas. Ejecuta… (+7 more)

### Community 4 - "Entregable B: modulos y contrato base"
Cohesion: 0.24
Nodes (11): ABC, BaseLLMClient, Abstract contract that every provider-specific LLM client must implement., Contrato que todo cliente de LLM debe cumplir, sin importar el proveedor real…, Google Gemini provider client (free tier, no credit card required)., Groq provider client (free tier, no credit card required). Groq expone una API…, AsyncLLMManager: punto de entrada unico y agnostico al proveedor (patron…, OpenAI provider client. Nota: OpenAI no tiene free tier (requiere tarjeta y… (+3 more)

### Community 5 - "AsyncLLMManager (Factory) y OpenAIClient"
Cohesion: 0.19
Nodes (6): BaseModel, AsyncLLMManager, Recibe un LLMConfig, arma internamente el cliente concreto y delega en el., OpenAIClient, LLMConfig, Configuration required to instantiate a provider client via the factory.

### Community 6 - "Clientes concretos: streaming y ChatMessage"
Cohesion: 0.22
Nodes (7): Content, Genera la respuesta token a token (modo streaming)., GeminiClient, Gemini separa el system prompt del resto y llama 'model' al rol del asistente., ChatMessage, A single message in a conversation., field_validator

### Community 7 - "GroqClient y ModelResponse"
Cohesion: 0.29
Nodes (4): Genera una respuesta completa (modo normal, no streaming)., GroqClient, ModelResponse, Uniform response returned by every client, success or failure.

### Community 8 - "Fase 2 Componente B: validacion estructurada"
Cohesion: 0.33
Nodes (6): EntityExtraction, BaseModel, Componente B - Fase 2: Validacion estructurada y resiliencia en cadenas.…, Contrato de datos validado que debe devolver el LLM., Extrae entidades del texto de forma validada y resiliente ante fallos., run_validated_chain()

### Community 9 - "Script de validacion main.py (Fase 1)"
Cohesion: 0.60
Nodes (4): main(), probar_proveedor(), Script de validacion del Unified Async LLM Client. Carga las variables de…, LLMConfig

### Community 10 - "Fase 2 Componente A: refactorizacion LCEL"
Cohesion: 0.50
Nodes (4): build_chain(), main(), Componente A - Fase 2: Refactorizacion a LCEL Asincrono. Reemplaza la llamada…, Compone prompt | model | parser usando el operador LCEL.

## Knowledge Gaps
- **24 isolated node(s):** `Google Gemini (proveedor gratuito recomendado)`, `Groq (proveedor gratuito recomendado)`, `Ollama local (proveedor gratuito recomendado)`, `OpenAI (proveedor de pago)`, `Anthropic (proveedor de pago)` (+19 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ChatMessage` connect `Clientes concretos: streaming y ChatMessage` to `Entregable B: modulos y contrato base`, `AsyncLLMManager (Factory) y OpenAIClient`, `GroqClient y ModelResponse`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Why does `Modulo 1: La interfaz base - conexion y abstraccion de LLMs` connect `Panorama del curso y spec de Fase 1` to `Entregable A: orquestador concurrente`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `Provider` connect `Entregable B: modulos y contrato base` to `Fase 2 Componente C: pipeline validado (codigo)`, `AsyncLLMManager (Factory) y OpenAIClient`, `Clientes concretos: streaming y ChatMessage`, `GroqClient y ModelResponse`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `ChatMessage` (e.g. with `BaseLLMClient` and `GeminiClient`) actually correct?**
  _`ChatMessage` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `ModelResponse` (e.g. with `BaseLLMClient` and `GeminiClient`) actually correct?**
  _`ModelResponse` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `BaseLLMClient` (e.g. with `ChatMessage` and `ModelResponse`) actually correct?**
  _`BaseLLMClient` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `AsyncLLMManager` (e.g. with `BaseLLMClient` and `GeminiClient`) actually correct?**
  _`AsyncLLMManager` has 8 INFERRED edges - model-reasoned connections that need verification._