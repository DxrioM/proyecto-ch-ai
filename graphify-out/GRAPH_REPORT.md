# Graph Report - .  (2026-09-07)

## Corpus Check
- 17 files · ~16,100 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 295 nodes · 475 edges · 19 communities (15 shown, 4 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 46 edges (avg confidence: 0.67)
- Token cost: 110,000 input · 8,500 output

## Community Hubs (Navigation)
- Entregable B: clientes LLM y contrato base
- Fase 2: validacion estructurada y pipeline (codigo)
- Fase 3 Componente D: pipeline RAG (ingest + rag_chain)
- Spec Fase 3: RAG y vector DBs
- Panorama del curso y spec Fase 1
- Dataset RAG: Sistema de Pedidos Online (ficticio)
- Entregable A: orquestador concurrente
- Documentacion Fase 2: pipeline validado
- Fase 3 Componente B: chunking (codigo)
- Fase 3 Componente A: calculo de similitud (codigo)
- Script de validacion main.py (Fase 1)
- Fase 2 Componente A: refactorizacion LCEL
- conftest.py (setup de tests)
- Spec Componente A (Fase 2)
- Decision: reemplazo de AsyncLLMManager por LangChain
- Import BaseModel (ejercicio B, Fase 2)

## God Nodes (most connected - your core abstractions)
1. `ChatMessage` - 25 edges
2. `ModelResponse` - 18 edges
3. `BaseLLMClient` - 16 edges
4. `AsyncLLMManager` - 14 edges
5. `GeminiClient` - 12 edges
6. `Provider` - 12 edges
7. `VectorMemoryManager` - 12 edges
8. `GroqClient` - 11 edges
9. `OpenAIClient` - 11 edges
10. `process_text()` - 11 edges

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
- **Flujo RAG end-to-end: chunking, persistencia vectorial y generacion grounded** — contexto_fase3_documentprocessor, contexto_fase3_vectormemorymanager, fase3_rag_local_readme_ragresponse [INFERRED 0.85]
- **Mecanismo de consistencia de embeddings indexar/consultar** — contexto_fase3_defaultembeddingfunction, contexto_fase3_embeddings_no_coincidentes, contexto_fase3_chromadb [INFERRED 0.85]
- **Stack de backend ficticio del Sistema de Pedidos Online (PostgreSQL, Redis, RabbitMQ)** — fase3_rag_local_data_arquitectura_postgresql, fase3_rag_local_data_arquitectura_redis, fase3_rag_local_data_arquitectura_rabbitmq [INFERRED 0.85]
- **Synthetic Resilience Testing via Dependency Injection** — tests_test_fase2_resilience, fase2_pipeline_validado_readme_process_text, fase2_pipeline_validado_readme_run_validated_chain, fase2_pipeline_validado_readme_resilient_model_injection, fase2_pipeline_validado_readme_runnable_falso [INFERRED 0.85]
- **Fase 2 — Tres componentes evaluables del curso AI Engineering** — contexto_fase2_componente_a, contexto_fase2_componente_b, contexto_fase2_componente_c [EXTRACTED 1.00]
- **Demo 1: gather + timeout sobre tres llamadas simuladas a modelos** — entregable_a_orquestador_orquestador_concurrente_orquestar_tres_modelos, entregable_a_orquestador_orquestador_concurrente_gpt_4_call, entregable_a_orquestador_orquestador_concurrente_claude_3_call, entregable_a_orquestador_orquestador_concurrente_local_llama_call [INFERRED 0.85]
- **Proveedores de IA gratuitos recomendados para Entregable B** — contexto_fase1_provider_gemini, contexto_fase1_provider_groq, contexto_fase1_provider_ollama [INFERRED 0.75]

## Communities (19 total, 4 thin omitted)

### Community 0 - "Entregable B: clientes LLM y contrato base"
Cohesion: 0.10
Nodes (28): ABC, BaseModel, Content, BaseLLMClient, Abstract contract that every provider-specific LLM client must implement., Contrato que todo cliente de LLM debe cumplir, sin importar el proveedor real…, Genera una respuesta completa (modo normal, no streaming)., Genera la respuesta token a token (modo streaming). (+20 more)

### Community 1 - "Fase 2: validacion estructurada y pipeline (codigo)"
Cohesion: 0.07
Nodes (42): Enum, EntityExtraction, Runnable, Componente B - Fase 2: Validacion estructurada y resiliencia en cadenas.…, Contrato de datos validado que debe devolver el LLM., Extrae entidades del texto de forma validada y resiliente ante fallos.…, run_validated_chain(), build_chain() (+34 more)

### Community 2 - "Fase 3 Componente D: pipeline RAG (ingest + rag_chain)"
Cohesion: 0.07
Nodes (36): Any, Componente C - Fase 3: Persistencia local con ChromaDB (operaciones CRUD).…, Encapsula una coleccion de ChromaDB persistida en disco., Inserta o actualiza documentos. upsert (no add) para que una reingesta con los…, Busqueda por similitud semantica. Devuelve los n_results documentos mas…, Elimina documentos por ID., Cantidad de documentos actualmente en la coleccion., VectorMemoryManager (+28 more)

### Community 3 - "Spec Fase 3: RAG y vector DBs"
Cohesion: 0.07
Nodes (35): Contexto de Proyecto - Fase 3, ChromaDB PersistentClient (base vectorial local), Componente A - Embeddings y Similitud (consigna), Componente B - Chunking y preprocesamiento (consigna), Componente D - Pre-entrega 3: Sistema RAG local (consigna), Error 'contexto infinito' / Lost in the Middle, DefaultEmbeddingFunction (Sentence Transformers all-MiniLM-L6-v2 via ONNX), DocumentProcessor (chunking por tokens con tiktoken) (+27 more)

### Community 4 - "Panorama del curso y spec Fase 1"
Cohesion: 0.09
Nodes (23): Programa AI Engineering (8 fases), Especificacion Entregable A: Orquestador Concurrente de Modelos, Especificacion Entregable B: Cliente de LLM robusto y asincrono, Anthropic (proveedor de pago), Google Gemini (proveedor gratuito recomendado), Groq (proveedor gratuito recomendado), Ollama local (proveedor gratuito recomendado), OpenAI (proveedor de pago) (+15 more)

### Community 5 - "Dataset RAG: Sistema de Pedidos Online (ficticio)"
Cohesion: 0.14
Nodes (21): Arquitectura del Sistema de Pedidos Online (doc ficticio de ejemplo), Patron database-per-service (esquema propio por microservicio), FastAPI (API REST, Python 3.12), PostgreSQL 16 (persistencia principal), RabbitMQ (cola de mensajes asincronica), Redis (cache de sesiones y carrito de compras), Servicio de Catalogo, Servicio de Notificaciones (+13 more)

### Community 6 - "Entregable A: orquestador concurrente"
Cohesion: 0.17
Nodes (19): Evidencia de ejecucion (logs de consola Demo 1 y Demo 2), claude_3_call(), gpt_4_call(), llamada_simulada(), local_llama_call(), main(), orquestar_con_semaforo(), orquestar_tres_modelos() (+11 more)

### Community 7 - "Documentacion Fase 2: pipeline validado"
Cohesion: 0.21
Nodes (12): Componente B — Validacion estructurada y resiliencia en cadenas (consigna), Componente C — Pipeline de procesamiento validado (Pre-entrega 2, consigna), EntityExtraction (Pydantic schema, ejercicio TODO), Rationale: preferir proveedores gratuitos (Groq/Gemini) con soporte with_structured_output, with_retry(), with_structured_output(), chain.py, main.py (+4 more)

### Community 8 - "Fase 3 Componente B: chunking (codigo)"
Cohesion: 0.22
Nodes (6): DocumentProcessor, Componente B - Fase 3: Estrategias de chunking y preprocesamiento. Resuelve el…, Limpia y fragmenta texto en chunks acotados por cantidad de tokens., Limpia el texto eliminando espacios duplicados y saltos de linea innecesarios., Calcula la cantidad de tokens usando el tokenizer de tiktoken., Pipeline: limpieza -> fragmentacion. Basura entra, basura sale: nunca…

### Community 9 - "Fase 3 Componente A: calculo de similitud (codigo)"
Cohesion: 0.25
Nodes (10): analizar(), calcular_embeddings(), comparacion_lexica_vs_semantica(), Componente A - Fase 3: Embeddings y Similitud, la geometria del lenguaje.…, La comparacion mas fina y honesta del ejercicio: para cada trampa, la enfrenta…, Genera embeddings reales con el mismo modelo local que usan los Componentes C y…, Calcula la matriz de similitud coseno entre las 7 oraciones y devuelve (labels,…, Compara la similitud promedio DENTRO del cluster de concepto contra la… (+2 more)

### Community 10 - "Script de validacion main.py (Fase 1)"
Cohesion: 0.60
Nodes (4): main(), probar_proveedor(), Script de validacion del Unified Async LLM Client. Carga las variables de…, LLMConfig

### Community 11 - "Fase 2 Componente A: refactorizacion LCEL"
Cohesion: 0.50
Nodes (4): build_chain(), main(), Componente A - Fase 2: Refactorizacion a LCEL Asincrono. Reemplaza la llamada…, Compone prompt | model | parser usando el operador LCEL.

## Ambiguous Edges - Review These
- `Prueba: pregunta trampa (politica de reembolsos VIP, no en contexto)` → `Politicas de Soporte y SLA (doc ficticio de ejemplo)`  [AMBIGUOUS]
  fase3_rag_local/README.md · relation: conceptually_related_to

## Knowledge Gaps
- **27 isolated node(s):** `Google Gemini (proveedor gratuito recomendado)`, `Groq (proveedor gratuito recomendado)`, `Ollama local (proveedor gratuito recomendado)`, `OpenAI (proveedor de pago)`, `Anthropic (proveedor de pago)` (+22 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Prueba: pregunta trampa (politica de reembolsos VIP, no en contexto)` and `Politicas de Soporte y SLA (doc ficticio de ejemplo)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `RagResponse` connect `Fase 3 Componente D: pipeline RAG (ingest + rag_chain)` to `Entregable B: clientes LLM y contrato base`?**
  _High betweenness centrality (0.302) - this node is a cross-community bridge._
- **Why does `EntityExtraction` connect `Fase 2: validacion estructurada y pipeline (codigo)` to `Entregable B: clientes LLM y contrato base`?**
  _High betweenness centrality (0.191) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `ChatMessage` (e.g. with `BaseLLMClient` and `GeminiClient`) actually correct?**
  _`ChatMessage` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `ModelResponse` (e.g. with `BaseLLMClient` and `GeminiClient`) actually correct?**
  _`ModelResponse` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `BaseLLMClient` (e.g. with `ChatMessage` and `ModelResponse`) actually correct?**
  _`BaseLLMClient` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `AsyncLLMManager` (e.g. with `BaseLLMClient` and `GeminiClient`) actually correct?**
  _`AsyncLLMManager` has 8 INFERRED edges - model-reasoned connections that need verification._