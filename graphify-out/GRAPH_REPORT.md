# Graph Report - .  (2026-09-07)

## Corpus Check
- 5 files · ~17,253 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 333 nodes · 537 edges · 24 communities (19 shown, 5 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 52 edges (avg confidence: 0.67)
- Token cost: 52,000 input · 2,200 output

## Community Hubs (Navigation)
- Fase 3 Componentes C/D: pipeline RAG y almacenamiento vectorial
- Entregable B: clientes LLM y contrato base
- Fase 2: validacion estructurada y pipeline (codigo)
- Spec Fase 3: RAG y vector DBs
- Panorama del curso y spec Fase 1
- Entregable A: orquestador concurrente
- Dataset RAG: Sistema de Pedidos Online (ficticio)
- Documentacion Fase 2: pipeline validado
- Fase 3 Componente C: VectorMemoryManager (detalle)
- Fase 3 Componente A: calculo de similitud (codigo)
- Fase 2 Componente C: TechExtraction (schemas)
- Fase 3 Componente B: DocumentProcessor (detalle)
- Tests sinteticos Fase 3: manejo de errores ChromaDB
- Script de validacion main.py (Fase 1)
- Fase 2 Componente A: refactorizacion LCEL
- Dataset RAG: politicas de soporte (ficticio)
- conftest.py (setup de tests)
- Spec Componente A (Fase 2)
- Decision: reemplazo de AsyncLLMManager por LangChain
- Import BaseModel (ejercicio B, Fase 2)
- Import Path (utilidad)

## God Nodes (most connected - your core abstractions)
1. `ChatMessage` - 25 edges
2. `ModelResponse` - 18 edges
3. `BaseLLMClient` - 16 edges
4. `AsyncLLMManager` - 14 edges
5. `ingest()` - 14 edges
6. `get_rag_response()` - 14 edges
7. `GeminiClient` - 12 edges
8. `Provider` - 12 edges
9. `GroqClient` - 11 edges
10. `OpenAIClient` - 11 edges

## Surprising Connections (you probably didn't know these)
- `asyncio.Semaphore (control de flujo y rate limits)` --conceptually_related_to--> `orquestar_con_semaforo()`  [INFERRED]
  program-summary.pdf → entregable_a_orquestador/orquestador_concurrente.py
- `asyncio.timeout (seguro contra latencia infinita)` --conceptually_related_to--> `orquestar_tres_modelos()`  [INFERRED]
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
- **Suite de tests sinteticos de Fase 3 (sin llamar a la API real)** — tests_test_fase3_resilience, fase3_rag_local_rag_chain_get_rag_response, fase3_ejercicio_chromadb_vector_memory_manager_vectormemorymanager, fase3_rag_local_ingest_ingest, fase3_ejercicio_chunking_document_processor_documentprocessor [EXTRACTED 1.00]
- **Flujo RAG end-to-end: chunking, persistencia vectorial y generacion grounded** — contexto_fase3_documentprocessor, contexto_fase3_vectormemorymanager [INFERRED 0.85]
- **Mecanismo de consistencia de embeddings indexar/consultar** — contexto_fase3_defaultembeddingfunction, contexto_fase3_embeddings_no_coincidentes, contexto_fase3_chromadb [INFERRED 0.85]
- **Stack de backend ficticio del Sistema de Pedidos Online (PostgreSQL, Redis, RabbitMQ)** — fase3_rag_local_data_arquitectura_postgresql, fase3_rag_local_data_arquitectura_redis, fase3_rag_local_data_arquitectura_rabbitmq [INFERRED 0.85]
- **Synthetic Resilience Testing via Dependency Injection** — tests_test_fase2_resilience, fase2_pipeline_validado_readme_process_text, fase2_pipeline_validado_readme_run_validated_chain, fase2_pipeline_validado_readme_resilient_model_injection, fase2_pipeline_validado_readme_runnable_falso [INFERRED 0.85]
- **Fase 2 — Tres componentes evaluables del curso AI Engineering** — contexto_fase2_componente_a, contexto_fase2_componente_b, contexto_fase2_componente_c [EXTRACTED 1.00]
- **Demo 1: gather + timeout sobre tres llamadas simuladas a modelos** — entregable_a_orquestador_orquestador_concurrente_orquestar_tres_modelos, entregable_a_orquestador_orquestador_concurrente_gpt_4_call, entregable_a_orquestador_orquestador_concurrente_claude_3_call, entregable_a_orquestador_orquestador_concurrente_local_llama_call [INFERRED 0.85]
- **Proveedores de IA gratuitos recomendados para Entregable B** — contexto_fase1_provider_gemini, contexto_fase1_provider_groq, contexto_fase1_provider_ollama [INFERRED 0.75]

## Communities (24 total, 5 thin omitted)

### Community 0 - "Fase 3 Componentes C/D: pipeline RAG y almacenamiento vectorial"
Cohesion: 0.06
Nodes (49): DocumentProcessor, Componente C - Fase 3: Persistencia local con ChromaDB (operaciones CRUD).…, Componente B - Fase 3: Estrategias de chunking y preprocesamiento. Resuelve el…, Diagrama de flujo: busqueda semantica (query, embedding, similitud, ranking, top-k), _file_hash(), ingest(), _load_manifest(), Path (+41 more)

### Community 1 - "Entregable B: clientes LLM y contrato base"
Cohesion: 0.10
Nodes (28): ABC, BaseModel, Content, BaseLLMClient, Abstract contract that every provider-specific LLM client must implement., Contrato que todo cliente de LLM debe cumplir, sin importar el proveedor real…, Genera una respuesta completa (modo normal, no streaming)., Genera la respuesta token a token (modo streaming). (+20 more)

### Community 2 - "Fase 2: validacion estructurada y pipeline (codigo)"
Cohesion: 0.09
Nodes (34): EntityExtraction, Runnable, Componente B - Fase 2: Validacion estructurada y resiliencia en cadenas.…, Contrato de datos validado que debe devolver el LLM., Extrae entidades del texto de forma validada y resiliente ante fallos.…, run_validated_chain(), build_chain(), process_text() (+26 more)

### Community 3 - "Spec Fase 3: RAG y vector DBs"
Cohesion: 0.07
Nodes (36): Contexto de Proyecto - Fase 3, ChromaDB PersistentClient (base vectorial local), Componente A - Embeddings y Similitud (consigna), Componente B - Chunking y preprocesamiento (consigna), Componente D - Pre-entrega 3: Sistema RAG local (consigna), Error 'contexto infinito' / Lost in the Middle, DefaultEmbeddingFunction (Sentence Transformers all-MiniLM-L6-v2 via ONNX), DocumentProcessor (chunking por tokens con tiktoken) (+28 more)

### Community 4 - "Panorama del curso y spec Fase 1"
Cohesion: 0.09
Nodes (23): Programa AI Engineering (8 fases), Especificacion Entregable A: Orquestador Concurrente de Modelos, Especificacion Entregable B: Cliente de LLM robusto y asincrono, Anthropic (proveedor de pago), Google Gemini (proveedor gratuito recomendado), Groq (proveedor gratuito recomendado), Ollama local (proveedor gratuito recomendado), OpenAI (proveedor de pago) (+15 more)

### Community 5 - "Entregable A: orquestador concurrente"
Cohesion: 0.17
Nodes (19): Evidencia de ejecucion (logs de consola Demo 1 y Demo 2), claude_3_call(), gpt_4_call(), llamada_simulada(), local_llama_call(), main(), orquestar_con_semaforo(), orquestar_tres_modelos() (+11 more)

### Community 6 - "Dataset RAG: Sistema de Pedidos Online (ficticio)"
Cohesion: 0.14
Nodes (20): Arquitectura del Sistema de Pedidos Online (doc ficticio de ejemplo), Patron database-per-service (esquema propio por microservicio), FastAPI (API REST, Python 3.12), PostgreSQL 16 (persistencia principal), RabbitMQ (cola de mensajes asincronica), Redis (cache de sesiones y carrito de compras), Servicio de Catalogo, Servicio de Notificaciones (+12 more)

### Community 7 - "Documentacion Fase 2: pipeline validado"
Cohesion: 0.21
Nodes (12): Componente B — Validacion estructurada y resiliencia en cadenas (consigna), Componente C — Pipeline de procesamiento validado (Pre-entrega 2, consigna), EntityExtraction (Pydantic schema, ejercicio TODO), Rationale: preferir proveedores gratuitos (Groq/Gemini) con soporte with_structured_output, with_retry(), with_structured_output(), chain.py, main.py (+4 more)

### Community 8 - "Fase 3 Componente C: VectorMemoryManager (detalle)"
Cohesion: 0.18
Nodes (7): Any, Encapsula una coleccion de ChromaDB persistida en disco., Inserta o actualiza documentos. upsert (no add) para que una reingesta con los…, Busqueda por similitud semantica. Devuelve los n_results documentos mas…, Elimina documentos por ID., Cantidad de documentos actualmente en la coleccion., VectorMemoryManager

### Community 9 - "Fase 3 Componente A: calculo de similitud (codigo)"
Cohesion: 0.25
Nodes (10): analizar(), calcular_embeddings(), comparacion_lexica_vs_semantica(), Componente A - Fase 3: Embeddings y Similitud, la geometria del lenguaje.…, La comparacion mas fina y honesta del ejercicio: para cada trampa, la enfrenta…, Genera embeddings reales con el mismo modelo local que usan los Componentes C y…, Calcula la matriz de similitud coseno entre las 7 oraciones y devuelve (labels,…, Compara la similitud promedio DENTRO del cluster de concepto contra la… (+2 more)

### Community 10 - "Fase 2 Componente C: TechExtraction (schemas)"
Cohesion: 0.25
Nodes (8): Enum, NivelCriticidad, BaseModel, Contrato de datos del Pipeline de Extraccion de Entidades Tecnicas., Nivel de criticidad tecnica detectado en el texto., Salida estructurada y validada que debe devolver la cadena LCEL., TechExtraction, str

### Community 11 - "Fase 3 Componente B: DocumentProcessor (detalle)"
Cohesion: 0.28
Nodes (5): DocumentProcessor, Limpia y fragmenta texto en chunks acotados por cantidad de tokens., Limpia el texto eliminando espacios duplicados y saltos de linea innecesarios., Calcula la cantidad de tokens usando el tokenizer de tiktoken., Pipeline: limpieza -> fragmentacion. Basura entra, basura sale: nunca…

### Community 12 - "Tests sinteticos Fase 3: manejo de errores ChromaDB"
Cohesion: 0.25
Nodes (5): fixture, _FailingCollection, manager_con_coleccion_rota(), VectorMemoryManager, Doble falso de una coleccion de Chroma que siempre falla, para probar que…

### Community 13 - "Script de validacion main.py (Fase 1)"
Cohesion: 0.60
Nodes (4): main(), probar_proveedor(), Script de validacion del Unified Async LLM Client. Carga las variables de…, LLMConfig

### Community 14 - "Fase 2 Componente A: refactorizacion LCEL"
Cohesion: 0.50
Nodes (4): build_chain(), main(), Componente A - Fase 2: Refactorizacion a LCEL Asincrono. Reemplaza la llamada…, Compone prompt | model | parser usando el operador LCEL.

### Community 15 - "Dataset RAG: politicas de soporte (ficticio)"
Cohesion: 1.00
Nodes (3): Politicas de Soporte y SLA (doc ficticio de ejemplo), Escalamiento de Severidad 1 a #incidentes-criticos y on-call, SLA por severidad (1: <30min, 2: <4h habiles, 3: <2 dias habiles)

## Knowledge Gaps
- **26 isolated node(s):** `Google Gemini (proveedor gratuito recomendado)`, `Groq (proveedor gratuito recomendado)`, `Ollama local (proveedor gratuito recomendado)`, `OpenAI (proveedor de pago)`, `Anthropic (proveedor de pago)` (+21 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RagResponse` connect `Fase 3 Componentes C/D: pipeline RAG y almacenamiento vectorial` to `Entregable B: clientes LLM y contrato base`, `Tests sinteticos Fase 3: manejo de errores ChromaDB`?**
  _High betweenness centrality (0.268) - this node is a cross-community bridge._
- **Why does `EntityExtraction` connect `Fase 2: validacion estructurada y pipeline (codigo)` to `Entregable B: clientes LLM y contrato base`?**
  _High betweenness centrality (0.164) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `ChatMessage` (e.g. with `BaseLLMClient` and `GeminiClient`) actually correct?**
  _`ChatMessage` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `ModelResponse` (e.g. with `BaseLLMClient` and `GeminiClient`) actually correct?**
  _`ModelResponse` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `BaseLLMClient` (e.g. with `ChatMessage` and `ModelResponse`) actually correct?**
  _`BaseLLMClient` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `AsyncLLMManager` (e.g. with `BaseLLMClient` and `GeminiClient`) actually correct?**
  _`AsyncLLMManager` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Google Gemini (proveedor gratuito recomendado)`, `Groq (proveedor gratuito recomendado)`, `Ollama local (proveedor gratuito recomendado)` to the rest of the system?**
  _26 weakly-connected nodes found - possible documentation gaps or missing edges._