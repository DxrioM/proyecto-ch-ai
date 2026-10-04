# Graph Report - .  (2026-10-04)

## Corpus Check
- 12 files · ~36,622 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 637 nodes · 1041 edges · 47 communities (36 shown, 11 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 91 edges (avg confidence: 0.61)
- Token cost: 96,000 input · 5,200 output

## Community Hubs (Navigation)
- Fase 3 Componentes C/D: pipeline RAG y almacenamiento vectorial
- Entregable B: clientes LLM y contrato base
- Fase 3/4/5: detalle VectorMemoryManager y grafos compilados
- Spec Fase 5: agente ReAct con LangGraph
- Panorama del curso y spec Fase 1
- Fase 2: validacion estructurada y pipeline (codigo)
- Fase 4 Componente D: embeddings y retriever (detalle)
- Dataset RAG: Sistema de Pedidos Online (ficticio)
- Spec Fase 3: RAG y vector DBs
- Fase 4 Componente A: setup Pinecone (detalle)
- Fase 6: graph.py (Supervisor y modelos)
- Fase 6: SupervisorDecision y tests sinteticos (detalle)
- Tests sinteticos Fase 4 (detalle)
- Fase 4 Componente B: IngestionPipeline (detalle)
- Fase 6: main.py, compile_graph y notebook demo
- Fase 6: agente investigador (Vector DB Fase 3/4)
- Fase 4 Componente D: evaluate.py (Precision/Recall)
- Documentacion Fase 2: pipeline validado
- Fase 4 Componente D: PineconeRetriever (detalle)
- Fase 3 Componente B: DocumentProcessor (detalle)
- Fase 3 Componente A: calculo de similitud (codigo)
- Fase 4 Componente B: metadatos y batching (detalle)
- Fase 6: agente analista (calculo de estadisticas)
- Spec Componente D (Fase 4): golden set y metricas
- Documentacion Fase 6: Supervisor, create_react_agent y bug de calculo
- Spec Componente A (Fase 4): setup Pinecone
- Fase 2 Componente A: refactorizacion LCEL
- Documentacion Fase 6: OrchestratorState y bug de truncamiento
- Spec Componente B (Fase 4): ingesta masiva
- conftest.py (setup de tests)
- Spec Componente A (Fase 2)
- Decision: reemplazo de AsyncLLMManager por LangChain
- Concepto: contexto infinito (Fase 3)
- Concepto: BM25 + embeddings hibrido (Fase 4)
- Concepto: F1-Score (Fase 4)
- Objetivo de la Fase 4
- Concepto: Precision@k (Fase 4)
- Concepto: Recall@k (Fase 4)
- Import BaseModel (ejercicio B, Fase 2)
- Import Path (ingest.py, Fase 4)

## God Nodes (most connected - your core abstractions)
1. `ChatMessage` - 25 edges
2. `IngestionPipeline` - 23 edges
3. `MockPineconeIndex` - 19 edges
4. `ModelResponse` - 18 edges
5. `PineconeRetriever` - 18 edges
6. `BaseLLMClient` - 16 edges
7. `LocalChromaEmbeddings` - 16 edges
8. `AsyncLLMManager` - 14 edges
9. `ingest()` - 14 edges
10. `get_rag_response()` - 14 edges

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
- **Flujo de delegacion Supervisor-Investigador-Analista** — readme_supervisor, readme_investigador, readme_analista, readme_orchestratorstate [EXTRACTED 1.00]
- **Errores comunes evitados (orquestacion multi-agente, Fase 6)** — fase6_orquestador_multiagente_readme_supervisor_infinito, fase6_orquestador_multiagente_readme_bug_contribuciones_truncadas, fase6_orquestador_multiagente_readme_bug_supervisor_calculo, fase6_orquestador_multiagente_readme_max_contribuciones [INFERRED 0.85]
- **Arquitectura del agente ReAct (Fase 5): StateGraph + tools_condition + AsyncSqliteSaver + herramientas** — fase5_agente_langgraph_readme_stategraph, fase5_agente_langgraph_readme_asyncsqlitesaver, fase5_agente_langgraph_readme_buscar_pedidos, fase5_agente_langgraph_readme_obtener_detalle_pedido [INFERRED 0.85]
- **Topología jerárquica Supervisor + agentes especialistas (Fase 6, spec)** — contexto_fase6_supervisor, contexto_fase6_research_agent, contexto_fase6_analyst_agent [EXTRACTED 1.00]
- **Validacion end-to-end de Fase 4 contra Pinecone real: hallazgo y correccion de 2 bugs** — fase4_rag_pinecone_readme_estado, fase4_rag_pinecone_readme_bug_localchromaembeddings_float32, fase4_rag_pinecone_readme_bug_create_metadata_source, fase4_rag_pinecone_embeddings_localchromaembeddings, fase4_ejercicio_ingesta_masiva_ingestion_pipeline_ingestionpipeline_create_metadata [INFERRED 0.75]
- **Evaluacion cuantitativa Fase 4: golden set + Precision@5/Recall@5** — contexto_fase4_componente_d_golden_set, contexto_fase4_recall_at_k, contexto_fase4_precision_at_k [INFERRED 0.80]
- **Suite de tests sinteticos de Fase 3 (sin llamar a la API real)** — tests_test_fase3_resilience, fase3_rag_local_rag_chain_get_rag_response, fase3_ejercicio_chromadb_vector_memory_manager_vectormemorymanager, fase3_rag_local_ingest_ingest, fase3_ejercicio_chunking_document_processor_documentprocessor [EXTRACTED 1.00]
- **Flujo RAG end-to-end: chunking, persistencia vectorial y generacion grounded** — contexto_fase3_documentprocessor, contexto_fase3_vectormemorymanager [INFERRED 0.85]
- **Mecanismo de consistencia de embeddings indexar/consultar** — contexto_fase3_defaultembeddingfunction, contexto_fase3_embeddings_no_coincidentes, contexto_fase3_chromadb [INFERRED 0.85]
- **Stack de backend ficticio del Sistema de Pedidos Online (PostgreSQL, Redis, RabbitMQ)** — fase3_rag_local_data_arquitectura_postgresql, fase3_rag_local_data_arquitectura_redis, fase3_rag_local_data_arquitectura_rabbitmq [INFERRED 0.85]
- **Synthetic Resilience Testing via Dependency Injection** — tests_test_fase2_resilience, fase2_pipeline_validado_readme_process_text, fase2_pipeline_validado_readme_run_validated_chain, fase2_pipeline_validado_readme_resilient_model_injection, fase2_pipeline_validado_readme_runnable_falso [INFERRED 0.85]
- **Fase 2 — Tres componentes evaluables del curso AI Engineering** — contexto_fase2_componente_a, contexto_fase2_componente_b, contexto_fase2_componente_c [EXTRACTED 1.00]
- **Demo 1: gather + timeout sobre tres llamadas simuladas a modelos** — entregable_a_orquestador_orquestador_concurrente_orquestar_tres_modelos, entregable_a_orquestador_orquestador_concurrente_gpt_4_call, entregable_a_orquestador_orquestador_concurrente_claude_3_call, entregable_a_orquestador_orquestador_concurrente_local_llama_call [INFERRED 0.85]
- **Proveedores de IA gratuitos recomendados para Entregable B** — contexto_fase1_provider_gemini, contexto_fase1_provider_groq, contexto_fase1_provider_ollama [INFERRED 0.75]

## Communities (47 total, 11 thin omitted)

### Community 0 - "Fase 3 Componentes C/D: pipeline RAG y almacenamiento vectorial"
Cohesion: 0.05
Nodes (52): DocumentProcessor, Componente C - Fase 3: Persistencia local con ChromaDB (operaciones CRUD).…, Diagrama de flujo: busqueda semantica (query, embedding, similitud, ranking, top-k), _file_hash(), ingest(), _load_manifest(), Path, VectorMemoryManager (+44 more)

### Community 1 - "Entregable B: clientes LLM y contrato base"
Cohesion: 0.07
Nodes (40): ABC, BaseModel, Content, BaseLLMClient, Abstract contract that every provider-specific LLM client must implement., Contrato que todo cliente de LLM debe cumplir, sin importar el proveedor real…, Genera una respuesta completa (modo normal, no streaming)., Genera la respuesta token a token (modo streaming). (+32 more)

### Community 2 - "Fase 3/4/5: detalle VectorMemoryManager y grafos compilados"
Cohesion: 0.06
Nodes (35): Any, CompiledStateGraph, Encapsula una coleccion de ChromaDB persistida en disco., Inserta o actualiza documentos. upsert (no add) para que una reingesta con los…, Busqueda por similitud semantica. Devuelve los n_results documentos mas…, Elimina documentos por ID., Cantidad de documentos actualmente en la coleccion., VectorMemoryManager (+27 more)

### Community 3 - "Spec Fase 5: agente ReAct con LangGraph"
Cohesion: 0.07
Nodes (44): contexto_fase5.md — Pre-entrega 5: Agente de razonamiento cíclico con memoria persistente, buscar_pedidos(cliente_id=102) (ejemplo del spec), MessagesState (spec Fase 5), Ciclo ReAct / razonamiento cíclico, recursion_limit (spec, techo ej. 10 pasos), SqliteSaver (checkpointer sincrónico mencionado en el spec), StateGraph que hereda de MessagesState (spec Fase 5), thread_id (resiliencia de estado) (+36 more)

### Community 4 - "Panorama del curso y spec Fase 1"
Cohesion: 0.06
Nodes (42): Programa AI Engineering (8 fases), Especificacion Entregable A: Orquestador Concurrente de Modelos, Especificacion Entregable B: Cliente de LLM robusto y asincrono, Anthropic (proveedor de pago), Google Gemini (proveedor gratuito recomendado), Groq (proveedor gratuito recomendado), Ollama local (proveedor gratuito recomendado), OpenAI (proveedor de pago) (+34 more)

### Community 5 - "Fase 2: validacion estructurada y pipeline (codigo)"
Cohesion: 0.09
Nodes (34): EntityExtraction, Runnable, Componente B - Fase 2: Validacion estructurada y resiliencia en cadenas.…, Contrato de datos validado que debe devolver el LLM., Extrae entidades del texto de forma validada y resiliente ante fallos.…, run_validated_chain(), build_chain(), process_text() (+26 more)

### Community 6 - "Fase 4 Componente D: embeddings y retriever (detalle)"
Cohesion: 0.11
Nodes (15): BM25Retriever, Embeddings, LocalChromaEmbeddings, Adaptador LangChain para el modelo de embeddings local de la Fase 3. langchain-…, Embeddings 100% locales, sin API key, compatibles con la interfaz de LangChain…, Retriever vectorial propio sobre el SDK nativo de Pinecone. Sustituye a…, build_bm25_retriever(), Document (+7 more)

### Community 7 - "Dataset RAG: Sistema de Pedidos Online (ficticio)"
Cohesion: 0.12
Nodes (24): Arquitectura del Sistema de Pedidos Online (doc ficticio de ejemplo), Patron database-per-service (esquema propio por microservicio), FastAPI (API REST, Python 3.12), PostgreSQL 16 (persistencia principal), RabbitMQ (cola de mensajes asincronica), Redis (cache de sesiones y carrito de compras), Servicio de Catalogo, Servicio de Notificaciones (+16 more)

### Community 8 - "Spec Fase 3: RAG y vector DBs"
Cohesion: 0.11
Nodes (23): ChromaDB PersistentClient (base vectorial local), Componente A - Embeddings y Similitud (consigna), Componente B - Chunking y preprocesamiento (consigna), Componente D - Pre-entrega 3: Sistema RAG local (consigna), DefaultEmbeddingFunction (Sentence Transformers all-MiniLM-L6-v2 via ONNX), DocumentProcessor (chunking por tokens con tiktoken), Error 'embeddings no coincidentes' - mismo modelo para indexar y consultar, Estrategia de gratuidad: embeddings locales + ChromaDB + Groq/Gemini (+15 more)

### Community 9 - "Fase 4 Componente A: setup Pinecone (detalle)"
Cohesion: 0.15
Nodes (16): ensure_index_exists(), Componente A - Fase 4: Pinecone Serverless, persistencia vectorial en la nube.…, Crea el indice Serverless si no existe (idempotente) y espera a que este listo.…, Configura la infraestructura de Pinecone Serverless y realiza una carga inicial…, setup_vector_infrastructure(), _file_hash(), ingest(), _load_json() (+8 more)

### Community 10 - "Fase 6: graph.py (Supervisor y modelos)"
Cohesion: 0.13
Nodes (18): BaseMessage, build_graph(), _build_specialist_model(), _build_supervisor_model(), _formatear_contribuciones(), Any, Fase 6: grafo del orquestador multi-agente (topologia jerarquica). Un nodo…, Arma el grafo (sin compilar). Inyectable en dos niveles, para poder testear sin… (+10 more)

### Community 11 - "Fase 6: SupervisorDecision y tests sinteticos (detalle)"
Cohesion: 0.21
Nodes (11): Salida estructurada del Supervisor: a quien rutear, por que, y -solo si ya…, SupervisorDecision, _FakeSpecialistAgent, _FakeSupervisor, Tests sinteticos para la Fase 6 (orquestador multi-agente con Supervisor). 1.…, El Supervisor Infinito que advierte la consigna: si un Supervisor (real o con…, Devuelve una secuencia prefijada de decisiones, una por llamada., Reemplaza un especialista entero (bypassea create_react_agent y el LLM real):… (+3 more)

### Community 12 - "Tests sinteticos Fase 4 (detalle)"
Cohesion: 0.18
Nodes (11): _FakeAdapter, _FakeEmbeddingsBatch, _FakeProcessor, Path, Tests sinteticos para la Fase 4 (Pinecone, ingesta masiva, RAG hibrido). No…, Doble falso con la misma interfaz que PineconeAsyncAdapter., _run_ingest(), _SistemaPerfecto (+3 more)

### Community 13 - "Fase 4 Componente B: IngestionPipeline (detalle)"
Cohesion: 0.20
Nodes (11): IngestionPipeline, main(), MockPineconeIndex, Componente B - Fase 4: Ingesta masiva y gestion de metadatos avanzados.…, Busqueda vectorial acotada por categoria, usando el operador de filtro $eq para…, Doble falso de un indice Pinecone, para desarrollar y testear el pipeline sin…, Encapsula la ingesta masiva: metadatos enriquecidos + batching + busqueda…, test_create_metadata_snippet_length_is_configurable() (+3 more)

### Community 14 - "Fase 6: main.py, compile_graph y notebook demo"
Cohesion: 0.17
Nodes (14): fase6_orquestador_multiagente/demo_flujo_delegacion.ipynb, compile_graph(), Conveniencia: arma y compila el grafo (sin checkpointer - esta fase no pide…, main(), _message_to_dict(), Fase 6: demo del flujo de delegacion Supervisor -> Investigador -> Analista ->…, Diagrama Mermaid del grafo (app.get_graph().draw_mermaid()), fase6_orquestador_multiagente/traces/ejemplo_flujo_delegacion.json (+6 more)

### Community 15 - "Fase 6: agente investigador (Vector DB Fase 3/4)"
Cohesion: 0.15
Nodes (13): Contexto de Proyecto - Fase 3, Contexto de Proyecto - Fase 4: Escalabilidad documental (RAG avanzado y Pinecone), build_research_agent(), buscar_en_base_de_conocimiento(), _get_manager(), Any, tool, Agente de Busqueda/Investigacion. Herramienta: busqueda simulada sobre la… (+5 more)

### Community 16 - "Fase 4 Componente D: evaluate.py (Precision/Recall)"
Cohesion: 0.18
Nodes (11): cargar_golden_set(), evaluar(), Any, Path, Componente D - Fase 4: evaluate.py, Precision@k y Recall@k sobre un golden set.…, Contrato minimo que evaluar() necesita de un sistema de recuperacion: alcanza…, Calcula, para cada pregunta del golden set: - Recall@k: 1 si el documento…, Retriever (+3 more)

### Community 17 - "Documentacion Fase 2: pipeline validado"
Cohesion: 0.21
Nodes (12): Componente B — Validacion estructurada y resiliencia en cadenas (consigna), Componente C — Pipeline de procesamiento validado (Pre-entrega 2, consigna), EntityExtraction (Pydantic schema, ejercicio TODO), Rationale: preferir proveedores gratuitos (Groq/Gemini) con soporte with_structured_output, with_retry(), with_structured_output(), chain.py, main.py (+4 more)

### Community 18 - "Fase 4 Componente D: PineconeRetriever (detalle)"
Cohesion: 0.22
Nodes (8): BaseRetriever, CallbackManagerForRetrieverRun, PineconeRetriever, Document, Busca por similitud vectorial en un indice Pinecone y devuelve Document de…, _FakeEmbeddings, _FakeIndex, test_pinecone_retriever_builds_documents_from_matches()

### Community 19 - "Fase 3 Componente B: DocumentProcessor (detalle)"
Cohesion: 0.22
Nodes (6): DocumentProcessor, Componente B - Fase 3: Estrategias de chunking y preprocesamiento. Resuelve el…, Limpia y fragmenta texto en chunks acotados por cantidad de tokens., Limpia el texto eliminando espacios duplicados y saltos de linea innecesarios., Calcula la cantidad de tokens usando el tokenizer de tiktoken., Pipeline: limpieza -> fragmentacion. Basura entra, basura sale: nunca…

### Community 20 - "Fase 3 Componente A: calculo de similitud (codigo)"
Cohesion: 0.25
Nodes (10): analizar(), calcular_embeddings(), comparacion_lexica_vs_semantica(), Componente A - Fase 3: Embeddings y Similitud, la geometria del lenguaje.…, La comparacion mas fina y honesta del ejercicio: para cada trampa, la enfrenta…, Genera embeddings reales con el mismo modelo local que usan los Componentes C y…, Calcula la matriz de similitud coseno entre las 7 oraciones y devuelve (labels,…, Compara la similitud promedio DENTRO del cluster de concepto contra la… (+2 more)

### Community 21 - "Fase 4 Componente B: metadatos y batching (detalle)"
Cohesion: 0.24
Nodes (7): Any, Arma los metadatos enriquecidos de un documento. Guardar el texto (completo o…, Divide documents en batches y hace upsert de a lotes (nunca vector por vector:…, Bug encontrado en validacion real: IngestionPipeline.create_metadata() (Componente B) no tenia campo 'source', solo 'category', por lo que no habia forma de saber de que archivo vino cada chunk recuperado. Corregido agregando un parametro opcional extra_metadata (retrocompatible, no cambia el comportamiento/tests existentes del Componente B) para que el Componente D pudiera adjuntar el nombre del archivo fuente., Bug encontrado en validacion real: LocalChromaEmbeddings devolvia numpy.float32 en vez de float nativo de Python; el SDK de Pinecone no puede serializar eso a JSON y el upsert fallaba con PineconeTypeError. Corregido casteando a float()., Estado de este componente (fase4_rag_pinecone): validado end-to-end contra indice real 'proyecto-ch-ai-fase4' (Pinecone free tier). evaluate.py sobre golden set de 5 preguntas: Recall@5=1.00 (documento fuente correcto siempre primero en el ranking hibrido Pinecone+BM25); Precision@5=0.25, explicado como artefacto del corpus de prueba de solo 4 documentos (top_k=5 siempre devuelve los 4 documentos existentes), no un problema de calidad de recuperacion. Se encontraron y corrigieron 2 bugs reales durante esta validacion, no detectables sin conexion real a Pinecone., Que esta probado (fase4_rag_pinecone): tests sinteticos deterministas sin red (LocalChromaEmbeddings dimension 384, PineconeRetriever con indice falso, evaluate.evaluar() con sistemas falsos, idempotencia + limpieza de chunks huerfanos de ingest()) MAS validacion real end-to-end: setup_infra.py crea el indice real e idempotente, ingest.py sube el corpus completo, evaluate.py da Recall@5=1.00 sobre el golden set.

### Community 22 - "Fase 6: agente analista (calculo de estadisticas)"
Cohesion: 0.25
Nodes (8): build_analyst_agent(), calcular_estadisticas(), Any, tool, Agente de Analisis/Computo. Herramienta: calculos matematicos sobre valores…, Calcula estadisticas basicas (promedio, minimo, maximo, suma, cantidad) sobre…, Arma el sub-agente de analisis con create_react_agent., calcular_estadisticas (tool del Analista)

### Community 23 - "Spec Componente D (Fase 4): golden set y metricas"
Cohesion: 0.29
Nodes (8): Componente D - Pre-entrega 4: Sistema RAG escalable en la nube con Pinecone (consigna), Golden Set (preguntas + documento_id_esperado), Re-ranking con cross-encoders, EnsembleRetriever (LangChain), Estrategia de gratuidad Fase 4 (Pinecone free tier + embeddings locales + BM25 + Groq/Gemini), RRF - Reciprocal Rank Fusion, Componente C README - Metricas y recuperacion hibrida (repaso conceptual), Aplicacion concreta: RAGSystem + evaluate.py en fase4_rag_pinecone

### Community 24 - "Documentacion Fase 6: Supervisor, create_react_agent y bug de calculo"
Cohesion: 0.48
Nodes (7): Bug: el Supervisor calculaba el promedio el mismo con una conversion de unidades incorrecta (48h en vez de 16h) en lugar de delegar al Analista, SupervisorDecision (salida estructurada, Literal investigador/analista/FINISH), _ultima_instruccion() (aislamiento de contexto entre especialistas), Analista (especialista de analisis numerico), create_react_agent, Investigador (especialista de investigacion), Supervisor (nodo de ruteo dinamico)

### Community 25 - "Spec Componente A (Fase 4): setup Pinecone"
Cohesion: 0.33
Nodes (6): Componente A - Pinecone Serverless: persistencia vectorial en la nube (consigna), setup_vector_infrastructure() (enunciado Componente A), Error: ignorar namespaces (Pinecone), Error: metrica erronea, euclidiana vs coseno (Pinecone), Error: mismatch de dimensiones (Pinecone), Pinecone Serverless

### Community 26 - "Fase 2 Componente A: refactorizacion LCEL"
Cohesion: 0.50
Nodes (4): build_chain(), main(), Componente A - Fase 2: Refactorizacion a LCEL Asincrono. Reemplaza la llamada…, Compone prompt | model | parser usando el operador LCEL.

### Community 27 - "Documentacion Fase 6: OrchestratorState y bug de truncamiento"
Cohesion: 0.40
Nodes (5): Bug: resumenes truncados a 300 caracteres provocaban bucle casi infinito de re-investigacion, MAX_CONTRIBUCIONES (criterio de suficiencia estricto), El "Supervisor Infinito" (patron de error de orquestacion multi-agente), contribuciones (lista acumulativa de aportes por especialista), OrchestratorState

### Community 28 - "Spec Componente B (Fase 4): ingesta masiva"
Cohesion: 0.67
Nodes (3): Componente B - Ingesta masiva y gestion de metadatos avanzados (consigna), IngestionPipeline (enunciado Componente B), MockPineconeIndex (enunciado Componente B)

## Ambiguous Edges - Review These
- `contexto_fase5.md — Pre-entrega 5: Agente de razonamiento cíclico con memoria persistente` → `contexto_fasefinal.md — Entrega final: Sistema Intelligence de grado de producción (spec unicamente, sin implementacion aun)`  [AMBIGUOUS]
  contexto_fasefinal.md · relation: conceptually_related_to

## Knowledge Gaps
- **51 isolated node(s):** `Google Gemini (proveedor gratuito recomendado)`, `Groq (proveedor gratuito recomendado)`, `Ollama local (proveedor gratuito recomendado)`, `OpenAI (proveedor de pago)`, `Anthropic (proveedor de pago)` (+46 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `contexto_fase5.md — Pre-entrega 5: Agente de razonamiento cíclico con memoria persistente` and `contexto_fasefinal.md — Entrega final: Sistema Intelligence de grado de producción (spec unicamente, sin implementacion aun)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `RagResponse` connect `Fase 3 Componentes C/D: pipeline RAG y almacenamiento vectorial` to `Entregable B: clientes LLM y contrato base`?**
  _High betweenness centrality (0.172) - this node is a cross-community bridge._
- **Why does `SupervisorDecision` connect `Fase 6: SupervisorDecision y tests sinteticos (detalle)` to `Entregable B: clientes LLM y contrato base`, `Fase 6: graph.py (Supervisor y modelos)`?**
  _High betweenness centrality (0.117) - this node is a cross-community bridge._
- **Why does `EntityExtraction` connect `Fase 2: validacion estructurada y pipeline (codigo)` to `Entregable B: clientes LLM y contrato base`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `ChatMessage` (e.g. with `BaseLLMClient` and `GeminiClient`) actually correct?**
  _`ChatMessage` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `IngestionPipeline` (e.g. with `PineconeAsyncAdapter` and `_FakeAdapter`) actually correct?**
  _`IngestionPipeline` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `MockPineconeIndex` (e.g. with `_FakeAdapter` and `_FakeEmbeddings`) actually correct?**
  _`MockPineconeIndex` has 7 INFERRED edges - model-reasoned connections that need verification._