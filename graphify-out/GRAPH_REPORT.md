# Graph Report - .  (2026-08-10)

## Corpus Check
- Corpus is ~4,157 words - fits in a single context window. You may not need a graph.

## Summary
- 116 nodes · 229 edges · 8 communities (7 shown, 1 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 32 edges (avg confidence: 0.62)
- Token cost: 480,000 input · 19,000 output

## Community Hubs (Navigation)
- Entregable B: modulos y contrato base
- Documentacion y proveedores de Entregable B
- Entregable A: orquestador concurrente
- Clientes concretos: streaming y validacion
- Panorama del curso y spec de Entregable A
- AsyncLLMManager (Factory) y main.py
- Dependencia python-dotenv

## God Nodes (most connected - your core abstractions)
1. `ChatMessage` - 26 edges
2. `ModelResponse` - 18 edges
3. `BaseLLMClient` - 16 edges
4. `AsyncLLMManager` - 16 edges
5. `Provider` - 13 edges
6. `GeminiClient` - 12 edges
7. `GroqClient` - 11 edges
8. `OpenAIClient` - 11 edges
9. `orquestar_tres_modelos()` - 10 edges
10. `LLMConfig` - 9 edges

## Surprising Connections (you probably didn't know these)
- `asyncio.Semaphore (control de flujo y rate limits)` --conceptually_related_to--> `orquestar_con_semaforo()`  [INFERRED]
  program-summary.pdf → entregable_a_orquestador/orquestador_concurrente.py
- `asyncio.timeout (seguro contra latencia infinita)` --conceptually_related_to--> `orquestar_tres_modelos()`  [INFERRED]
  program-summary.pdf → entregable_a_orquestador/orquestador_concurrente.py
- `Ejercicio: Orquestador Concurrente de Modelos (practica Modulo 1)` --conceptually_related_to--> `orquestar_tres_modelos()`  [INFERRED]
  program-summary.pdf → entregable_a_orquestador/orquestador_concurrente.py
- `Modulo 1: La interfaz base - conexion y abstraccion de LLMs` --conceptually_related_to--> `BaseLLMClient (ABC)`  [INFERRED]
  program-summary.pdf → README.md
- `Factory Pattern para seleccion de cliente LLM` --conceptually_related_to--> `AsyncLLMManager (Factory)`  [INFERRED]
  program-summary.pdf → README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Demo 1: gather + timeout sobre tres llamadas simuladas a modelos** — entregable_a_orquestador_orquestador_concurrente_orquestar_tres_modelos, entregable_a_orquestador_orquestador_concurrente_gpt_4_call, entregable_a_orquestador_orquestador_concurrente_claude_3_call, entregable_a_orquestador_orquestador_concurrente_local_llama_call [INFERRED 0.85]
- **Componentes de la arquitectura Unified Async LLM Client** — readme_chatmessage, readme_llmconfig, readme_modelresponse, readme_basellmclient, readme_asyncllmmanager, readme_openaiclient, readme_geminiclient, readme_groqclient [INFERRED 0.85]
- **Proveedores de IA gratuitos recomendados para Entregable B** — contexto_fase1_provider_gemini, contexto_fase1_provider_groq, contexto_fase1_provider_ollama [INFERRED 0.75]

## Communities (8 total, 1 thin omitted)

### Community 0 - "Entregable B: modulos y contrato base"
Cohesion: 0.16
Nodes (17): ABC, BaseLLMClient, Abstract contract that every provider-specific LLM client must implement., Contrato que todo cliente de LLM debe cumplir, sin importar el proveedor real…, Genera una respuesta completa (modo normal, no streaming)., Google Gemini provider client (free tier, no credit card required)., GroqClient, Groq provider client (free tier, no credit card required). Groq expone una API… (+9 more)

### Community 1 - "Documentacion y proveedores de Entregable B"
Cohesion: 0.15
Nodes (21): Especificacion Entregable B: Cliente de LLM robusto y asincrono, Anthropic (proveedor de pago), Google Gemini (proveedor gratuito recomendado), Groq (proveedor gratuito recomendado), Ollama local (proveedor gratuito recomendado), OpenAI (proveedor de pago), Notebook de referencia: Pista_Pre_entrega_1_Cliente_de_LLM_robusto_y_asincrono.ipynb, Factory Pattern para seleccion de cliente LLM (+13 more)

### Community 2 - "Entregable A: orquestador concurrente"
Cohesion: 0.17
Nodes (19): Evidencia de ejecucion (logs de consola Demo 1 y Demo 2), claude_3_call(), gpt_4_call(), llamada_simulada(), local_llama_call(), main(), orquestar_con_semaforo(), orquestar_tres_modelos() (+11 more)

### Community 3 - "Clientes concretos: streaming y validacion"
Cohesion: 0.17
Nodes (8): Content, Genera la respuesta token a token (modo streaming)., GeminiClient, Gemini separa el system prompt del resto y llama 'model' al rol del asistente., OpenAIClient, ChatMessage, A single message in a conversation., field_validator

### Community 4 - "Panorama del curso y spec de Entregable A"
Cohesion: 0.13
Nodes (16): Programa AI Engineering (8 fases), Especificacion Entregable A: Orquestador Concurrente de Modelos, Curso AI Engineering (Coderhouse, 8 modulos, 30 horas), asyncio.gather (patron de concurrencia), asyncio.Semaphore (control de flujo y rate limits), Modulo 1: La interfaz base - conexion y abstraccion de LLMs, Modulo 2: Encadenamiento logico - orquestacion con LangChain (LCEL), Modulo 3: Persistencia de datos y vector DBs (+8 more)

### Community 5 - "AsyncLLMManager (Factory) y main.py"
Cohesion: 0.24
Nodes (8): BaseModel, AsyncLLMManager, Recibe un LLMConfig, arma internamente el cliente concreto y delega en el., main(), probar_proveedor(), Script de validacion del Unified Async LLM Client. Carga las variables de…, LLMConfig, Configuration required to instantiate a provider client via the factory.

## Knowledge Gaps
- **16 isolated node(s):** `Entregable A - Orquestador Concurrente de Modelos`, `Ollama local (proveedor gratuito recomendado)`, `Anthropic (proveedor de pago)`, `Notebook de referencia: Pista_Pre_entrega_1_Cliente_de_LLM_robusto_y_asincrono.ipynb`, `python-dotenv>=1.0 (dependencia)` (+11 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Modulo 1: La interfaz base - conexion y abstraccion de LLMs` connect `Panorama del curso y spec de Entregable A` to `Documentacion y proveedores de Entregable B`, `Entregable A: orquestador concurrente`?**
  _High betweenness centrality (0.146) - this node is a cross-community bridge._
- **Why does `ChatMessage` connect `Clientes concretos: streaming y validacion` to `Entregable B: modulos y contrato base`, `AsyncLLMManager (Factory) y main.py`?**
  _High betweenness centrality (0.087) - this node is a cross-community bridge._
- **Why does `orquestar_tres_modelos()` connect `Entregable A: orquestador concurrente` to `Panorama del curso y spec de Entregable A`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `ChatMessage` (e.g. with `BaseLLMClient` and `GeminiClient`) actually correct?**
  _`ChatMessage` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `ModelResponse` (e.g. with `BaseLLMClient` and `GeminiClient`) actually correct?**
  _`ModelResponse` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `BaseLLMClient` (e.g. with `ChatMessage` and `ModelResponse`) actually correct?**
  _`BaseLLMClient` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `AsyncLLMManager` (e.g. with `BaseLLMClient` and `GeminiClient`) actually correct?**
  _`AsyncLLMManager` has 8 INFERRED edges - model-reasoned connections that need verification._