# Graph Report - .  (2026-09-07)

## Corpus Check
- 16 files · ~25,465 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 479 nodes · 805 edges · 27 communities (20 shown, 7 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 85 edges (avg confidence: 0.63)
- Token cost: 113,000 input · 6,300 output

## Community Hubs (Navigation)
- Fase 3 Componentes C/D: pipeline RAG y almacenamiento vectorial
- Fase 4: IngestionPipeline, PineconeRetriever y tests sinteticos
- Entregable B: clientes LLM y contrato base
- Fase 2: validacion estructurada y pipeline (codigo)
- Fase 4 Componentes A/D: setup Pinecone, ingesta y RAGSystem
- Documentacion Fase 4: Pinecone y RAG hibrido
- Panorama del curso y spec Fase 1
- Dataset RAG: Sistema de Pedidos Online (ficticio)
- Spec Fase 3: RAG y vector DBs
- Fase 3 Componente C: VectorMemoryManager (detalle)
- Documentacion Fase 2: pipeline validado
- Fase 3 Componente A: calculo de similitud (codigo)
- Fase 4 Componente D: evaluate.py (Precision/Recall)
- Fase 3 Componente B: DocumentProcessor (detalle)
- Script de validacion main.py (Fase 1)
- Fase 2 Componente A: refactorizacion LCEL
- conftest.py (setup de tests)
- Spec Componente A (Fase 2)
- Decision: reemplazo de AsyncLLMManager por LangChain
- Concepto: contexto infinito (Fase 3)
- Objetivo de la Fase 4
- Import BaseModel (ejercicio B, Fase 2)
- Import Path (utilidad)

## God Nodes (most connected - your core abstractions)
1. `ChatMessage` - 25 edges
2. `IngestionPipeline` - 23 edges
3. `MockPineconeIndex` - 19 edges
4. `ModelResponse` - 18 edges
5. `PineconeRetriever` - 18 edges
6. `BaseLLMClient` - 16 edges
7. `LocalChromaEmbeddings` - 15 edges
8. `AsyncLLMManager` - 14 edges
9. `ingest()` - 14 edges
10. `get_rag_response()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `PineconeRetriever (BaseRetriever propio sobre SDK nativo de pinecone)` --semantically_similar_to--> `VectorMemoryManager`  [INFERRED] [semantically similar]
  fase4_rag_pinecone/README.md → fase3_ejercicio_chromadb/vector_memory_manager.py
- `asyncio.timeout (seguro contra latencia infinita)` --conceptually_related_to--> `orquestar_tres_modelos()`  [INFERRED]
  program-summary.pdf → entregable_a_orquestador/orquestador_concurrente.py
- `asyncio.Semaphore (control de flujo y rate limits)` --conceptually_related_to--> `orquestar_con_semaforo()`  [INFERRED]
  program-summary.pdf → entregable_a_orquestador/orquestador_concurrente.py
- `Ejercicio: Orquestador Concurrente de Modelos (practica Modulo 1)` --conceptually_related_to--> `orquestar_tres_modelos()`  [INFERRED]
  program-summary.pdf → entregable_a_orquestador/orquestador_concurrente.py
- `Modulo 1: La interfaz base - conexion y abstraccion de LLMs` --conceptually_related_to--> `Programa AI Engineering (8 fases)`  [INFERRED]
  program-summary.pdf → contexto_fase1.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Recuperacion hibrida Fase 4: Pinecone + BM25 via EnsembleRetriever** — fase4_rag_pinecone_readme_ragsystem, fase4_rag_pinecone_readme_pineconeretriever, contexto_fase4_ensembleretriever, requirements_rank_bm25 [INFERRED 0.85]
- **Workaround Python 3.14: BaseRetriever propio en vez de langchain-pinecone** — fase4_rag_pinecone_readme_incompatibilidad_langchain_pinecone, fase4_rag_pinecone_readme_pineconeretriever, fase4_rag_pinecone_readme_localchromaembeddings, requirements_langchain_pinecone_omitted [INFERRED 0.90]
- **Evaluacion cuantitativa Fase 4: golden set + Precision@5/Recall@5** — fase4_rag_pinecone_readme_evaluate_py, contexto_fase4_componente_d_golden_set, contexto_fase4_recall_at_k, contexto_fase4_precision_at_k [INFERRED 0.80]
- **Suite de tests sinteticos de Fase 3 (sin llamar a la API real)** — tests_test_fase3_resilience, fase3_rag_local_rag_chain_get_rag_response, fase3_ejercicio_chromadb_vector_memory_manager_vectormemorymanager, fase3_rag_local_ingest_ingest, fase3_ejercicio_chunking_document_processor_documentprocessor [EXTRACTED 1.00]
- **Flujo RAG end-to-end: chunking, persistencia vectorial y generacion grounded** — contexto_fase3_documentprocessor, contexto_fase3_vectormemorymanager [INFERRED 0.85]
- **Mecanismo de consistencia de embeddings indexar/consultar** — contexto_fase3_defaultembeddingfunction, contexto_fase3_embeddings_no_coincidentes, contexto_fase3_chromadb [INFERRED 0.85]
- **Stack de backend ficticio del Sistema de Pedidos Online (PostgreSQL, Redis, RabbitMQ)** — fase3_rag_local_data_arquitectura_postgresql, fase3_rag_local_data_arquitectura_redis, fase3_rag_local_data_arquitectura_rabbitmq [INFERRED 0.85]
- **Synthetic Resilience Testing via Dependency Injection** — tests_test_fase2_resilience, fase2_pipeline_validado_readme_process_text, fase2_pipeline_validado_readme_run_validated_chain, fase2_pipeline_validado_readme_resilient_model_injection, fase2_pipeline_validado_readme_runnable_falso [INFERRED 0.85]
- **Fase 2 — Tres componentes evaluables del curso AI Engineering** — contexto_fase2_componente_a, contexto_fase2_componente_b, contexto_fase2_componente_c [EXTRACTED 1.00]
- **Demo 1: gather + timeout sobre tres llamadas simuladas a modelos** — entregable_a_orquestador_orquestador_concurrente_orquestar_tres_modelos, entregable_a_orquestador_orquestador_concurrente_gpt_4_call, entregable_a_orquestador_orquestador_concurrente_claude_3_call, entregable_a_orquestador_orquestador_concurrente_local_llama_call [INFERRED 0.85]
- **Proveedores de IA gratuitos recomendados para Entregable B** — contexto_fase1_provider_gemini, contexto_fase1_provider_groq, contexto_fase1_provider_ollama [INFERRED 0.75]

## Communities (27 total, 7 thin omitted)

### Community 0 - "Fase 3 Componentes C/D: pipeline RAG y almacenamiento vectorial"
Cohesion: 0.05
Nodes (53): DocumentProcessor, Componente C - Fase 3: Persistencia local con ChromaDB (operaciones CRUD).…, Componente B - Fase 3: Estrategias de chunking y preprocesamiento. Resuelve el…, Diagrama de flujo: busqueda semantica (query, embedding, similitud, ranking, top-k), _file_hash(), ingest(), _load_manifest(), Path (+45 more)

### Community 1 - "Fase 4: IngestionPipeline, PineconeRetriever y tests sinteticos"
Cohesion: 0.08
Nodes (35): BaseRetriever, CallbackManagerForRetrieverRun, IngestionPipeline, main(), MockPineconeIndex, Any, Componente B - Fase 4: Ingesta masiva y gestion de metadatos avanzados.…, Busqueda vectorial acotada por categoria, usando el operador de filtro $eq para… (+27 more)

### Community 2 - "Entregable B: clientes LLM y contrato base"
Cohesion: 0.10
Nodes (29): ABC, BaseModel, Content, BaseLLMClient, Abstract contract that every provider-specific LLM client must implement., Contrato que todo cliente de LLM debe cumplir, sin importar el proveedor real…, Genera una respuesta completa (modo normal, no streaming)., Genera la respuesta token a token (modo streaming). (+21 more)

### Community 3 - "Fase 2: validacion estructurada y pipeline (codigo)"
Cohesion: 0.07
Nodes (42): EntityExtraction, Runnable, Componente B - Fase 2: Validacion estructurada y resiliencia en cadenas.…, Contrato de datos validado que debe devolver el LLM., Extrae entidades del texto de forma validada y resiliente ante fallos.…, run_validated_chain(), build_chain(), process_text() (+34 more)

### Community 4 - "Fase 4 Componentes A/D: setup Pinecone, ingesta y RAGSystem"
Cohesion: 0.07
Nodes (31): BM25Retriever, Embeddings, ensure_index_exists(), Componente A - Fase 4: Pinecone Serverless, persistencia vectorial en la nube.…, Crea el indice Serverless si no existe (idempotente) y espera a que este listo.…, Configura la infraestructura de Pinecone Serverless y realiza una carga inicial…, setup_vector_infrastructure(), LocalChromaEmbeddings (+23 more)

### Community 5 - "Documentacion Fase 4: Pinecone y RAG hibrido"
Cohesion: 0.07
Nodes (45): Contexto de Proyecto - Fase 3, Contexto de Proyecto - Fase 4: Escalabilidad documental (RAG avanzado y Pinecone), Busqueda hibrida: combinar BM25 + embeddings, Componente A - Pinecone Serverless: persistencia vectorial en la nube (consigna), setup_vector_infrastructure() (enunciado Componente A), Componente B - Ingesta masiva y gestion de metadatos avanzados (consigna), IngestionPipeline (enunciado Componente B), MockPineconeIndex (enunciado Componente B) (+37 more)

### Community 6 - "Panorama del curso y spec Fase 1"
Cohesion: 0.06
Nodes (42): Programa AI Engineering (8 fases), Especificacion Entregable A: Orquestador Concurrente de Modelos, Especificacion Entregable B: Cliente de LLM robusto y asincrono, Anthropic (proveedor de pago), Google Gemini (proveedor gratuito recomendado), Groq (proveedor gratuito recomendado), Ollama local (proveedor gratuito recomendado), OpenAI (proveedor de pago) (+34 more)

### Community 7 - "Dataset RAG: Sistema de Pedidos Online (ficticio)"
Cohesion: 0.12
Nodes (24): Arquitectura del Sistema de Pedidos Online (doc ficticio de ejemplo), Patron database-per-service (esquema propio por microservicio), FastAPI (API REST, Python 3.12), PostgreSQL 16 (persistencia principal), RabbitMQ (cola de mensajes asincronica), Redis (cache de sesiones y carrito de compras), Servicio de Catalogo, Servicio de Notificaciones (+16 more)

### Community 8 - "Spec Fase 3: RAG y vector DBs"
Cohesion: 0.11
Nodes (23): ChromaDB PersistentClient (base vectorial local), Componente A - Embeddings y Similitud (consigna), Componente B - Chunking y preprocesamiento (consigna), Componente D - Pre-entrega 3: Sistema RAG local (consigna), DefaultEmbeddingFunction (Sentence Transformers all-MiniLM-L6-v2 via ONNX), DocumentProcessor (chunking por tokens con tiktoken), Error 'embeddings no coincidentes' - mismo modelo para indexar y consultar, Estrategia de gratuidad: embeddings locales + ChromaDB + Groq/Gemini (+15 more)

### Community 9 - "Fase 3 Componente C: VectorMemoryManager (detalle)"
Cohesion: 0.18
Nodes (7): Any, Encapsula una coleccion de ChromaDB persistida en disco., Inserta o actualiza documentos. upsert (no add) para que una reingesta con los…, Busqueda por similitud semantica. Devuelve los n_results documentos mas…, Elimina documentos por ID., Cantidad de documentos actualmente en la coleccion., VectorMemoryManager

### Community 10 - "Documentacion Fase 2: pipeline validado"
Cohesion: 0.21
Nodes (11): Componente B — Validacion estructurada y resiliencia en cadenas (consigna), Componente C — Pipeline de procesamiento validado (Pre-entrega 2, consigna), EntityExtraction (Pydantic schema, ejercicio TODO), Rationale: preferir proveedores gratuitos (Groq/Gemini) con soporte with_structured_output, with_retry(), with_structured_output(), chain.py, main.py (+3 more)

### Community 11 - "Fase 3 Componente A: calculo de similitud (codigo)"
Cohesion: 0.25
Nodes (10): analizar(), calcular_embeddings(), comparacion_lexica_vs_semantica(), Componente A - Fase 3: Embeddings y Similitud, la geometria del lenguaje.…, La comparacion mas fina y honesta del ejercicio: para cada trampa, la enfrenta…, Genera embeddings reales con el mismo modelo local que usan los Componentes C y…, Calcula la matriz de similitud coseno entre las 7 oraciones y devuelve (labels,…, Compara la similitud promedio DENTRO del cluster de concepto contra la… (+2 more)

### Community 12 - "Fase 4 Componente D: evaluate.py (Precision/Recall)"
Cohesion: 0.24
Nodes (9): cargar_golden_set(), evaluar(), Any, Path, Componente D - Fase 4: evaluate.py, Precision@k y Recall@k sobre un golden set.…, Contrato minimo que evaluar() necesita de un sistema de recuperacion: alcanza…, Calcula, para cada pregunta del golden set: - Recall@k: 1 si el documento…, Retriever (+1 more)

### Community 13 - "Fase 3 Componente B: DocumentProcessor (detalle)"
Cohesion: 0.28
Nodes (5): DocumentProcessor, Limpia y fragmenta texto en chunks acotados por cantidad de tokens., Limpia el texto eliminando espacios duplicados y saltos de linea innecesarios., Calcula la cantidad de tokens usando el tokenizer de tiktoken., Pipeline: limpieza -> fragmentacion. Basura entra, basura sale: nunca…

### Community 14 - "Script de validacion main.py (Fase 1)"
Cohesion: 0.60
Nodes (4): main(), probar_proveedor(), Script de validacion del Unified Async LLM Client. Carga las variables de…, LLMConfig

### Community 15 - "Fase 2 Componente A: refactorizacion LCEL"
Cohesion: 0.50
Nodes (4): build_chain(), main(), Componente A - Fase 2: Refactorizacion a LCEL Asincrono. Reemplaza la llamada…, Compone prompt | model | parser usando el operador LCEL.

## Knowledge Gaps
- **31 isolated node(s):** `Google Gemini (proveedor gratuito recomendado)`, `Groq (proveedor gratuito recomendado)`, `Ollama local (proveedor gratuito recomendado)`, `OpenAI (proveedor de pago)`, `Anthropic (proveedor de pago)` (+26 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RagResponse` connect `Fase 3 Componentes C/D: pipeline RAG y almacenamiento vectorial` to `Entregable B: clientes LLM y contrato base`?**
  _High betweenness centrality (0.276) - this node is a cross-community bridge._
- **Why does `VectorMemoryManager` connect `Fase 3 Componente C: VectorMemoryManager (detalle)` to `Fase 3 Componentes C/D: pipeline RAG y almacenamiento vectorial`, `Documentacion Fase 4: Pinecone y RAG hibrido`?**
  _High betweenness centrality (0.218) - this node is a cross-community bridge._
- **Why does `PineconeRetriever (BaseRetriever propio sobre SDK nativo de pinecone)` connect `Documentacion Fase 4: Pinecone y RAG hibrido` to `Fase 3 Componente C: VectorMemoryManager (detalle)`?**
  _High betweenness centrality (0.192) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `ChatMessage` (e.g. with `BaseLLMClient` and `GeminiClient`) actually correct?**
  _`ChatMessage` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `IngestionPipeline` (e.g. with `PineconeAsyncAdapter` and `_FakeAdapter`) actually correct?**
  _`IngestionPipeline` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `MockPineconeIndex` (e.g. with `_FakeAdapter` and `_FakeEmbeddings`) actually correct?**
  _`MockPineconeIndex` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `ModelResponse` (e.g. with `BaseLLMClient` and `GeminiClient`) actually correct?**
  _`ModelResponse` has 5 INFERRED edges - model-reasoned connections that need verification._