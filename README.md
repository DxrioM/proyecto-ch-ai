# Proyecto AI Engineering

Proyecto de 8 fases del curso "AI Engineering". Cada fase se documenta en su
propio `contexto_faseN.md` y se implementa en su propia carpeta. Este README
cubre las Fases 1 a 5; a medida que se aprueben las siguientes fases se van
agregando sus secciones.

- Fase 1: [contexto_fase1.md](contexto_fase1.md) — interfaz base, conexion y
  abstraccion de LLMs.
- Fase 2: [contexto_fase2.md](contexto_fase2.md) — encadenamiento logico,
  orquestacion con LangChain.
- Fase 3: [contexto_fase3.md](contexto_fase3.md) — persistencia de datos y
  vector DBs (RAG).
- Fase 4: [contexto_fase4.md](contexto_fase4.md) — escalabilidad documental,
  RAG avanzado y Pinecone.
- Fase 5: [contexto_fase5.md](contexto_fase5.md) — razonamiento autonomo,
  agente ReAct con LangGraph.
- Fase 6: [contexto_fase6.md](contexto_fase6.md) — sistemas multi-agente,
  colaboracion y especializacion.

## Estructura

```
proyecto_ch_ai/
├── .env                          # claves reales (NO se versiona)
├── .env.example                  # mismas claves, sin valores
├── .gitignore
├── conftest.py                   # hace importable la raiz del repo para pytest
├── requirements.txt
├── tests/
│   └── test_fase2_resilience.py  # tests sinteticos de with_retry() / ValidationError
├── entregable_a_orquestador/            # Fase 1 - Entregable A
│   ├── orquestador_concurrente.py
│   ├── evidencia_ejecucion.log   # salida de consola capturada
│   └── entregable_a_evidencia.pdf
├── entregable_b_llm_client/             # Fase 1 - Entregable B
│   ├── schemas.py                # ChatMessage, LLMConfig, ModelResponse (Pydantic)
│   ├── base_client.py            # BaseLLMClient (ABC)
│   ├── gemini_client.py
│   ├── groq_client.py
│   ├── openai_client.py
│   ├── llm_manager.py            # AsyncLLMManager (Factory)
│   └── main.py                   # script de validacion (modo normal + streaming)
├── fase2_lcel_refactor/                 # Fase 2 - Componente A
│   └── main.py                   # prompt | model | StrOutputParser, con ainvoke
├── fase2_ejercicio_validacion/          # Fase 2 - Componente B
│   └── entity_extraction.py      # with_structured_output + with_retry
├── fase2_pipeline_validado/             # Fase 2 - Componente C (Pre-entrega 2)
│   ├── schemas.py                # TechExtraction (Pydantic)
│   ├── chain.py                  # cadena LCEL + process_text()
│   ├── main.py                   # mini-script de prueba
│   └── README.md                 # detalle del pipeline + ejemplo de salida
├── fase3_embeddings_similitud/          # Fase 3 - Componente A
│   ├── embeddings_similitud.py   # embeddings reales + similitud coseno (sklearn)
│   └── componente_a_evidencia.pdf
├── fase3_ejercicio_chunking/            # Fase 3 - Componente B
│   └── document_processor.py     # chunking por tokens (tiktoken + RecursiveCharacterTextSplitter)
├── fase3_ejercicio_chromadb/            # Fase 3 - Componente C
│   └── vector_memory_manager.py  # ChromaDB CRUD (upsert/query/delete)
├── fase3_rag_local/                     # Fase 3 - Componente D (Pre-entrega 3)
│   ├── data/                     # dataset de ejemplo (.md)
│   ├── ingest.py                 # ingesta idempotente: chunking + ChromaDB
│   ├── rag_chain.py              # retriever + cadena LCEL grounded (RagResponse)
│   ├── main.py                   # get_rag_response() + pregunta valida + pregunta trampa
│   └── README.md
├── fase4_ejercicio_pinecone_setup/      # Fase 4 - Componente A
│   └── setup_infra.py            # crea/verifica indice Pinecone Serverless (idempotente)
├── fase4_ejercicio_ingesta_masiva/      # Fase 4 - Componente B
│   └── ingestion_pipeline.py     # IngestionPipeline: batching + metadatos + filtro por categoria
├── fase4_metricas_recuperacion_hibrida/ # Fase 4 - Componente C (repaso conceptual)
│   └── README.md                 # Precision/Recall, BM25+embeddings, RRF, cross-encoders
├── fase4_rag_pinecone/                  # Fase 4 - Componente D (Pre-entrega 4)
│   ├── data/                     # reutiliza el corpus de fase3_rag_local/data
│   ├── golden_set.json           # 5 preguntas con documento fuente esperado
│   ├── embeddings.py             # adaptador LangChain sobre el embedding local de la Fase 3
│   ├── pinecone_retriever.py     # BaseRetriever propio sobre el SDK nativo de Pinecone
│   ├── ingest.py                 # chunking + embeddings + upsert idempotente a Pinecone
│   ├── rag_system.py             # RAGSystem: EnsembleRetriever (Pinecone + BM25)
│   ├── evaluate.py                # Precision@5 / Recall@5 sobre el golden set
│   └── README.md                 # incluye pasos para replicar el indice
├── fase5_agente_langgraph/              # Fase 5 - Pre-entrega 5
│   ├── tools.py                  # buscar_pedidos / obtener_detalle_pedido (@tool)
│   ├── graph.py                  # StateGraph: nodo modelo + ToolNode + tools_condition
│   ├── main.py                   # demo de 3 turnos + guarda la traza
│   ├── traces/ejemplo_traza.json # traza ReAct real (evidencia)
│   └── README.md
└── fase6_orquestador_multiagente/       # Fase 6 - Pre-entrega 6
    ├── state.py                  # OrchestratorState: next_agent + contribuciones
    ├── agents/
    │   ├── research_agent.py     # busca en la Vector DB de la Fase 3
    │   └── analyst_agent.py      # calcula estadisticas sobre datos investigados
    ├── graph.py                  # Supervisor (structured output) + aristas condicionales
    ├── main.py                   # demo del flujo de delegacion + guarda la traza
    ├── demo_flujo_delegacion.ipynb  # notebook ejecutado, paso a paso
    ├── traces/ejemplo_flujo_delegacion.json
    └── README.md                 # incluye diagrama Mermaid del grafo
```

## Requisitos

- Python 3.12+
- Un entorno virtual (`.venv`)

## Instalacion

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Entregable A — Orquestador Concurrente de Modelos

Simulacion pura (no llama APIs reales): tres corrutinas (`gpt_4_call`,
`claude_3_call`, `local_llama_call`) simulan latencia con `asyncio.sleep`.

- Demo 1: las tres corren en paralelo con `asyncio.gather`, acotadas por
  `asyncio.timeout(2.0)`. Como `local_llama_call` tarda 3.0s, se dispara
  `TimeoutError`, se captura y el programa sigue vivo.
- Demo 2: 10 llamadas simuladas se lanzan a la vez, pero un
  `asyncio.Semaphore(2)` limita a 2 ejecuciones concurrentes por vez.

Ejecutar:

```bash
python entregable_a_orquestador/orquestador_concurrente.py
```

La evidencia de una corrida ya quedo capturada en
`entregable_a_orquestador/evidencia_ejecucion.log` y compilada junto con el
codigo en `entregable_a_orquestador/entregable_a_evidencia.pdf` (el
entregable en formato PDF pedido por la consigna).

## Entregable B — Cliente de LLM robusto y asincrono

Cliente unificado ("Unified Async LLM Client") con interfaz comun para
distintos proveedores, 100% asincrono (`async`/`await`), con streaming y
validacion con Pydantic.

Proveedores implementados:

- **Gemini** (`google-genai`) — gratis, sin tarjeta.
- **Groq** (`groq`) — gratis, sin tarjeta; sirve modelos Llama.
- **OpenAI** (`openai`) — de pago; se incluye principalmente como prueba de
  resiliencia: si no se configura `OPENAI_API_KEY` (o es invalida), el
  cliente debe devolver el error dentro de `ModelResponse.error` (o como
  chunk de streaming) en vez de romper el programa.

### Variables de entorno

Copiar `.env.example` a `.env` y completar las que se vayan a usar:

| Variable | Proveedor | Obligatoria |
|---|---|---|
| `GOOGLE_API_KEY` | Gemini (`aistudio.google.com/apikey`) | Para probar Gemini |
| `GROQ_API_KEY` | Groq (`console.groq.com`) | Para probar Groq |
| `OPENAI_API_KEY` | OpenAI | Opcional (a proposito, para la prueba de resiliencia) |

### Ejecutar el script de validacion

Desde la raiz del proyecto (usa import relativo dentro del paquete):

```bash
python -m entregable_b_llm_client.main
```

El script:

1. Carga `.env`.
2. Por cada proveedor con key configurada, crea un `AsyncLLMManager` y hace
   la pregunta "Que es la entropia?" en modo normal y en modo streaming.
3. Prueba OpenAI a proposito sin key valida (si no se configuro
   `OPENAI_API_KEY`) para demostrar el manejo de errores sin crash.

### Arquitectura

- `ChatMessage`, `LLMConfig`, `ModelResponse`: modelos Pydantic para validar
  entrada/salida antes de tocar cualquier SDK.
- `BaseLLMClient` (ABC): contrato comun (`generate`, `generate_stream`) que
  cada cliente de proveedor debe cumplir.
- `OpenAIClient` / `GeminiClient` / `GroqClient`: implementan el contrato
  usando el SDK async oficial de cada proveedor, capturando siempre las
  excepciones propias del SDK y devolviendo un `ModelResponse` con `error`
  seteado (nunca dejan escapar la excepcion).
- `AsyncLLMManager` (Factory): recibe un `LLMConfig` y arma internamente el
  cliente correcto; el resto del codigo solo habla con el manager, agnostico
  al proveedor.

### Errores comunes evitados

- **Bloqueo del event loop**: todos los clientes usan exclusivamente los
  SDKs async (`AsyncOpenAI`, `genai.Client(...).aio`, `AsyncGroq`).
- **Fuga de excepciones**: ninguna excepcion de proveedor (rate limit, error
  de conexion, key invalida) rompe el programa; siempre vuelve como
  `ModelResponse.error` o como chunk de error en streaming.

---

# Fase 2 — Encadenamiento logico: orquestacion con LangChain

Reemplaza el `AsyncLLMManager` propio de la Fase 1 por cadenas declarativas
de LangChain (LCEL). Ver [contexto_fase2.md](contexto_fase2.md) para el
detalle completo de la consigna. Proveedor usado en los tres componentes:
**Groq** (`ChatGroq`, gratis, sin tarjeta), modelo `openai/gpt-oss-120b`.

## Componente A — Refactorizacion a LCEL Asincrono

`fase2_lcel_refactor/main.py`: reemplaza la llamada manual al SDK del
Modulo 1 por una cadena `prompt | model | StrOutputParser()`, con
`ChatPromptTemplate` (roles System/Human) y ejecucion asincrona
(`await chain.ainvoke({"pregunta": "..."})`). El resultado es texto plano,
no un `AIMessage`.

```bash
python fase2_lcel_refactor/main.py
```

## Componente B — Validacion estructurada y resiliencia

`fase2_ejercicio_validacion/entity_extraction.py`: resuelve el ejercicio de
la catedra (`with_structured_output` + `with_retry`), adaptado de
`ChatOpenAI` a `ChatGroq`. Define `EntityExtraction` (Pydantic: `topic`,
`entities`, `sentiment_score` entre 0 y 1, `complexity_level` opcional),
arma `structured_llm = llm.with_structured_output(EntityExtraction)` y
`resilient_llm = structured_llm.with_retry(stop_after_attempt=3,
wait_exponential_jitter=True)`, y ejecuta la cadena dentro de un
`try/except` que nunca deja escapar la excepcion.

```bash
python fase2_ejercicio_validacion/entity_extraction.py
```

## Componente C — Pipeline de Extraccion de Entidades Tecnicas (Pre-entrega 2)

El entregable principal de la Fase 2. Ver el detalle, el ejemplo de salida
JSON y el resultado de la prueba de estres en
[fase2_pipeline_validado/README.md](fase2_pipeline_validado/README.md).

```bash
python -m fase2_pipeline_validado.main
```

## Variables de entorno (Fase 2)

Reutiliza las mismas variables de la Fase 1 (`.env` en la raiz). Los tres
componentes de la Fase 2 solo necesitan `GROQ_API_KEY`.

## Tests sinteticos de resiliencia

`tests/test_fase2_resilience.py` prueba `with_retry()` y el manejo de
`ValidationError` de los Componentes B y C con un modelo falso (no llama a
la API real ni gasta cuota). Ver el detalle en
[fase2_pipeline_validado/README.md](fase2_pipeline_validado/README.md#tests-sinteticos-sin-llamar-a-la-api-real).

```bash
python -m pytest tests/ -v
```

## Errores comunes evitados (especificos de LangChain)

- **Olvidar el `await`**: `chain.ainvoke(...)` devuelve una corrutina; sin
  `await` no se ejecuta la llamada.
- **Prompts hardcodeados**: nada de f-strings sueltas dentro de una cadena;
  siempre `ChatPromptTemplate`, para que LangChain gestione las variables de
  entrada y estas coincidan con las claves pasadas a `ainvoke`.
- **JSON invalido o incompleto del LLM**: `with_structured_output()` valida
  contra el esquema Pydantic; `with_retry()` reintenta ante ese fallo o ante
  errores transitorios de red/rate limit, en vez de romper el programa.

---

# Fase 3 — Persistencia de datos y vector DBs (RAG)

Agrega memoria de largo plazo: convierte texto en embeddings, los persiste
en ChromaDB local y los usa para recuperar contexto relevante antes de
generar una respuesta (Retrieval-Augmented Generation). El LLM y la cadena
LCEL de la Fase 2 se reutilizan tal cual para la etapa de generacion. Ver
[contexto_fase3.md](contexto_fase3.md) para el detalle completo.

Pila 100% gratuita: embeddings locales (`DefaultEmbeddingFunction` de
Chroma, Sentence Transformers `all-MiniLM-L6-v2` via ONNX, sin API key) +
ChromaDB `PersistentClient` (local, en disco) + Groq (`ChatGroq`) para la
generacion.

## Componente A — Embeddings y Similitud

`fase3_embeddings_similitud/`: 5 oraciones sobre el mismo concepto tecnico
con vocabulario distinto + 2 oraciones trampa, embeddings reales, matriz de
Similitud Coseno con `scikit-learn` y diagrama de flujo de busqueda
semantica. Entregable en PDF (`componente_a_evidencia.pdf`), generado a
partir de una corrida real. Ver
[fase3_embeddings_similitud/README.md](fase3_embeddings_similitud/README.md).

```bash
python fase3_embeddings_similitud/embeddings_similitud.py
```

## Componente B — Chunking y preprocesamiento

`fase3_ejercicio_chunking/document_processor.py`: `DocumentProcessor` con
limpieza de texto por regex + `RecursiveCharacterTextSplitter` midiendo
longitud por **tokens** (`tiktoken`, no caracteres), `chunk_size=500` /
`chunk_overlap=50`.

```bash
python fase3_ejercicio_chunking/document_processor.py
```

## Componente C — Persistencia local con ChromaDB (CRUD)

`fase3_ejercicio_chromadb/vector_memory_manager.py`: `VectorMemoryManager`
encapsula un `PersistentClient` de ChromaDB (persistencia real en disco) +
`get_or_create_collection` con `DefaultEmbeddingFunction`. Expone
`upsert_documents` (nunca `add`, para que una reingesta no falle por IDs
duplicados), `semantic_search` (con `include=["documents","metadatas","distances"]`)
y `delete_by_id`, todo con IDs deterministicos y manejo de `ChromaError`.

```bash
python fase3_ejercicio_chromadb/vector_memory_manager.py
```

## Componente D — Sistema RAG local (Pre-entrega 3)

El entregable principal de la Fase 3. Ingesta idempotente desde `data/` +
recuperacion por similitud (`top_k=4`) + generacion grounded con un prompt
"filtro de veracidad" (el modelo dice que no sabe si la respuesta no esta
en el contexto, nunca alucina) + salida validada con Pydantic
(`RagResponse`: `respuesta`, `fuentes`, `encontrado_en_contexto`). Detalle,
arquitectura y las dos pruebas obligatorias (pregunta valida + pregunta
trampa, con evidencia real) en
[fase3_rag_local/README.md](fase3_rag_local/README.md).

```bash
python -m fase3_rag_local.main
```

## Variables de entorno (Fase 3)

Reutiliza `GROQ_API_KEY` de las fases anteriores. Los embeddings son
locales y no necesitan ninguna key.

## Errores comunes evitados (especificos de RAG)

- **Embeddings no coincidentes**: `VectorMemoryManager` asocia la funcion
  de embedding a la coleccion una unica vez (`get_or_create_collection`);
  Chroma la reutiliza automaticamente tanto al indexar como al consultar,
  asi que es imposible que se desincronicen.
- **"Contexto infinito"**: `top_k` siempre acotado a 4 (entre 3 y 5) en la
  recuperacion, nunca se le pasan decenas de fragmentos al LLM.
- **Falta de idempotencia**: `ingest()` guarda un hash por archivo en
  `vectorstore/manifest.json`; si el archivo no cambio, no se re-fragmenta
  ni se re-embede. Si cambio y genero menos chunks que antes, borra los IDs
  viejos que sobran para no dejar contenido huerfano.
- **Alucinacion fuera de contexto**: el prompt de sistema instruye
  explicitamente a responder "no lo se" cuando la respuesta no esta en el
  contexto recuperado; probado con una pregunta trampa real (ver
  `fase3_rag_local/README.md`).

## Tests sinteticos (Fase 3)

`tests/test_fase3_resilience.py` prueba `get_rag_response()` (retry +
ValidationError, mismo patron que la Fase 2), el manejo de `ChromaError` de
`VectorMemoryManager`, la idempotencia real de `ingest()` (incluida la
rama que borra chunks huerfanos al achicarse un archivo, documentada pero
nunca antes ejercitada) y casos limite de `DocumentProcessor`.

```bash
python -m pytest tests/ -v
```

---

# Fase 4 — Escalabilidad documental: RAG avanzado y Pinecone

Escala el RAG local de la Fase 3 a la nube: Pinecone Serverless reemplaza a
ChromaDB, se agrega recuperacion **hibrida** (vectorial + BM25) y una capa
de evaluacion cuantitativa (`Precision@5` / `Recall@5`). El chunking, el
LLM de generacion y el corpus de ejemplo de la Fase 3 se reutilizan tal
cual. Ver [contexto_fase4.md](contexto_fase4.md) para el detalle completo.

> **Estado**: los 4 componentes estan completos y validados, incluida la
> Pre-entrega 4 end-to-end contra una cuenta real de Pinecone (free tier):
> `Recall@5 = 1.00` sobre el golden set (el documento correcto siempre
> aparecio primero en el ranking hibrido). Detalle completo en
> [fase4_rag_pinecone/README.md](fase4_rag_pinecone/README.md).

**Nota de compatibilidad**: `langchain-pinecone` (el paquete que sugiere la
consigna) todavia no tiene build para Python 3.14 en este entorno (depende
de `simsimd<4.0`, sin wheels para esa version). Se reemplaza por un
`BaseRetriever` propio sobre el SDK nativo de `pinecone`
(`fase4_rag_pinecone/pinecone_retriever.py`), que cumple el mismo contrato
y se combina con `BM25Retriever` exactamente igual. Detalle completo en
[fase4_rag_pinecone/README.md](fase4_rag_pinecone/README.md).

## Componente A — Pinecone Serverless

`fase4_ejercicio_pinecone_setup/setup_infra.py`: crea el indice Serverless
solo si no existe (`ensure_index_exists`, idempotente), espera a que este
listo, y hace un upsert de prueba en el namespace `dev-environment`
(separado de los datos reales del Componente D).

```bash
python fase4_ejercicio_pinecone_setup/setup_infra.py
```

## Componente B — Ingesta masiva y metadatos avanzados

`fase4_ejercicio_ingesta_masiva/ingestion_pipeline.py`: `IngestionPipeline`
sobre un `MockPineconeIndex` (no requiere cuenta real). Metadatos
enriquecidos (`category`, `author`, `ingested_at`, `char_count`), batching
(nunca vector por vector), y busqueda filtrada por categoria (`$eq`). Se
reutiliza tal cual en el Componente D contra Pinecone real.

```bash
python fase4_ejercicio_ingesta_masiva/ingestion_pipeline.py
```

## Componente C — Metricas y recuperacion hibrida (repaso conceptual)

No es un entregable con codigo propio. Ver
[fase4_metricas_recuperacion_hibrida/README.md](fase4_metricas_recuperacion_hibrida/README.md):
Precision vs Recall, por que combinar BM25 + embeddings, RRF, re-ranking
con cross-encoders — la base teorica que aplica el Componente D.

## Componente D — Sistema RAG escalable en la nube (Pre-entrega 4)

El entregable principal de la Fase 4. `RAGSystem` (`EnsembleRetriever`
combinando el `PineconeRetriever` propio + `BM25Retriever`) y `evaluate.py`
(`Precision@5`/`Recall@5` sobre un golden set de 5 preguntas). Reutiliza el
corpus de `fase3_rag_local/data/` para demostrar que es el mismo sistema
escalado a la nube. Detalle completo, pasos para replicar el indice de
Pinecone, y que esta validado hasta ahora en
[fase4_rag_pinecone/README.md](fase4_rag_pinecone/README.md).

```bash
python -m fase4_rag_pinecone.ingest
python -m fase4_rag_pinecone.evaluate
```

## Variables de entorno (Fase 4)

| Variable | Notas |
|---|---|
| `PINECONE_API_KEY` | Gratis, sin tarjeta — `app.pinecone.io` |

## Tests sinteticos (Fase 4)

`tests/test_fase4_resilience.py`: batching y filtrado de `IngestionPipeline`,
`PineconeRetriever` construyendo `Document` a partir de una respuesta con
la misma forma que el SDK real, `evaluate.evaluar()` con sistemas
perfectos/fallidos, e idempotencia + limpieza de chunks huerfanos de
`fase4_rag_pinecone.ingest()` — todo sin necesitar `PINECONE_API_KEY`.

```bash
python -m pytest tests/ -v
```

## Errores comunes evitados (especificos de Pinecone)

- **Mismatch de dimensiones**: el indice se crea con `dimension=384`,
  exactamente la que produce `LocalChromaEmbeddings`; nunca se mezclan
  embeddings de distintos modelos entre indexar y consultar.
- **Ignorar namespaces**: los datos de prueba del Componente A
  (`dev-environment`) y los datos reales del Componente D
  (`fase4-corpus`) viven en namespaces separados dentro del mismo indice.
- **Metrica erronea**: `metric="cosine"`, la correcta para embeddings de
  Sentence Transformers (nunca euclidiana).
- **IDs no deterministicos**: a diferencia del enunciado generico del
  Componente B (que usa `uuid4`), la ingesta real del Componente D usa IDs
  deterministicos (`id_generator` inyectable) para poder ser idempotente.

---

# Fase 5 — Razonamiento autonomo: agente ReAct con LangGraph

Pre-entrega 5: un agente que decide por si mismo cuando llamar a una
herramienta (sin rutas `if`/`else` manuales), encadena mas de una llamada a
herramientas para llegar a una conclusion, y recuerda interacciones previas
dentro de una misma sesion gracias a un checkpointer SQLite. Continua el
dominio ficticio del "Sistema de Pedidos Online" de las Fases 3 y 4, ahora
consultado por un agente en vez de por RAG. Ver
[contexto_fase5.md](contexto_fase5.md) para el detalle completo.

## Arquitectura

- **Herramientas** (`tools.py`): `buscar_pedidos(cliente_id)` y
  `obtener_detalle_pedido(pedido_id)`, decoradas con `@tool`. El LLM elige
  cual usar unicamente en base al docstring — nunca hay logica manual que
  decida por el.
- **Grafo** (`graph.py`): `StateGraph(MessagesState)` con un nodo `agent`
  (LLM con `bind_tools()`) y un nodo `tools` (`ToolNode`), conectados por
  una arista condicional (`tools_condition`) que rutea segun si el LLM
  pidio o no una `tool_call`.
- **Persistencia**: `AsyncSqliteSaver` (checkpointer SQLite asincrono) —
  con el mismo `thread_id`, el agente recuerda toda la conversacion previa.
- **Demo** (`main.py`): 3 turnos sobre el mismo `thread_id`,
  `recursion_limit=10`, guarda la traza completa en
  `traces/ejemplo_traza.json`.

## Como correrlo

Requiere `GROQ_API_KEY` en el `.env` (reutilizada de fases anteriores).

```bash
python -m fase5_agente_langgraph.main
```

## Evidencia (traza real, no simulada)

Ver el detalle completo en
[fase5_agente_langgraph/README.md](fase5_agente_langgraph/README.md) y la
traza cruda en
[fase5_agente_langgraph/traces/ejemplo_traza.json](fase5_agente_langgraph/traces/ejemplo_traza.json).
Resumen de los 3 turnos (mismo `thread_id`):

1. *"Cuantos pedidos tuvo el cliente 102 y cual fue el total?"* → el agente
   llama `buscar_pedidos(102)` → responde "3 pedidos, $14.500".
2. *"Y cual es el detalle del ultimo pedido?"* → **sin repetir el cliente**,
   el agente recuerda el contexto, deduce el ultimo `pedido_id` (5003) del
   turno anterior y llama `obtener_detalle_pedido(5003)` — razonamiento
   multi-paso real, con memoria entre turnos.
3. *"Cuantos pedidos tuvo el cliente 999?"* → la herramienta devuelve un
   error (cliente inexistente); el agente lo explica en vez de alucinar
   una respuesta — ciclo de retorno ante un error.

## Tests sinteticos (Fase 5)

`tests/test_fase5_agent.py`: las herramientas probadas de forma
determinista (exito y error, sin LLM), y el ruteo del grafo
(`tools_condition`) con un LLM falso — confirma que la herramienta real se
ejecuta cuando el modelo decide llamarla, que el grafo termina sin llamar a
nada cuando no hace falta, y que la memoria entre turnos con el mismo
`thread_id` efectivamente acumula el historial.

```bash
python -m pytest tests/ -v
```

## Errores comunes evitados (especificos de LangGraph)

- **Descripciones vagas**: los docstrings de `buscar_pedidos` y
  `obtener_detalle_pedido` explican que hace cada una, cuando usarla, y
  como se relacionan entre si (una alimenta el `pedido_id` de la otra).
- **Bucles infinitos**: `recursion_limit=10` en cada invocacion.
- **Excepciones que rompen el ciclo**: las herramientas devuelven
  `{"error": ...}` en vez de lanzar, para que el LLM pueda razonar sobre el
  fallo (mismo criterio de resiliencia que el resto del proyecto desde la
  Fase 1) en vez de que el programa se caiga.

---

# Fase 6 — Sistemas multi-agente: colaboracion y especializacion

Pre-entrega 6: un **Orquestador Multi-Agente de Analisis e Investigacion**
con topologia jerarquica. Un nodo Supervisor rutea dinamicamente entre dos
especialistas (Investigador y Analista) hasta decidir que la tarea esta
completa y sintetizar la respuesta final. Continua el dominio del "Sistema
de Pedidos Online": el Investigador consulta la Vector DB de la Fase 3, el
Analista procesa numericamente lo que trae el Investigador. Ver
[contexto_fase6.md](contexto_fase6.md) para el detalle completo.

## Arquitectura

- **Estado compartido** (`state.py`): `OrchestratorState` (hereda de
  `MessagesState`) con `next_agent` (a donde rutea la proxima arista
  condicional) y `contribuciones` (lista acumulativa de que aporto cada
  especialista — asi no se pierde el rastro de quien dijo que).
- **Especialistas** (`agents/`): `research_agent.py` (busca en la Vector DB
  de la Fase 3 — la consigna permite esta alternativa a Tavily) y
  `analyst_agent.py` (calcula estadisticas sobre datos ya investigados).
  Ambos armados con `create_react_agent` (su propio mini-ciclo ReAct).
- **Supervisor** (`graph.py`): decide el proximo paso con salida
  estructurada (`Literal["investigador", "analista", "FINISH"]`), mapeada
  a una arista condicional. Al decidir `FINISH`, tambien redacta la
  sintesis final.

## Topologia y manejo de conflictos

Jerarquica con Supervisor central (no un pipeline fijo ni agentes que se
llaman entre si): mantiene a los especialistas desacoplados, y centraliza
en el Supervisor la decision de reintentar, derivar al otro especialista, o
cerrar — nunca el usuario ve un resultado a medio terminar. Detalle
completo (y el diagrama Mermaid del grafo) en
[fase6_orquestador_multiagente/README.md](fase6_orquestador_multiagente/README.md).

## Como correrlo

```bash
python -m fase6_orquestador_multiagente.main
# o, paso a paso en un notebook:
jupyter nbconvert --to notebook --execute fase6_orquestador_multiagente/demo_flujo_delegacion.ipynb
```

## Evidencia: flujo de delegacion real

Pregunta: *"Investiga en la base de conocimiento los tiempos de respuesta
comprometidos por severidad de soporte, y calculame el promedio en horas."*

Supervisor → **investigador** (falta informacion factual) → encuentra el
SLA en `politicas_soporte.md` → Supervisor → **analista** (hay que
convertir unidades y calcular) → promedio = **6.83 horas** → Supervisor →
**FINISH** con la sintesis final. Traza completa en
[`fase6_orquestador_multiagente/traces/ejemplo_flujo_delegacion.json`](fase6_orquestador_multiagente/traces/ejemplo_flujo_delegacion.json)
y, paso a paso, en
[`demo_flujo_delegacion.ipynb`](fase6_orquestador_multiagente/demo_flujo_delegacion.ipynb).

## Tests sinteticos (Fase 6)

`tests/test_fase6_orchestrator.py`: herramientas deterministas, y el flujo
de delegacion completo con un Supervisor falso (decisiones prefijadas) y
especialistas falsos — confirma el ruteo investigador→analista→FINISH, que
los especialistas no se llaman cuando no hace falta, y que el criterio de
suficiencia estricto corta el ciclo aunque el Supervisor nunca decida
terminar por si solo.

```bash
python -m pytest tests/ -v
```

## Errores comunes evitados (especificos de orquestacion multi-agente)

- **El "Supervisor Infinito"**: `recursion_limit` externo + un criterio de
  suficiencia estricto (`MAX_CONTRIBUCIONES`) dentro del propio nodo
  Supervisor.
- **Contaminacion de contexto**: los especialistas no reciben todo el
  historial del sistema, solo la instruccion puntual que necesitan.
- **Resumenes truncados que mienten**: una version inicial truncaba las
  contribuciones a 300 caracteres, cortando tablas a mitad de fila — el
  Supervisor interpretaba que faltaba informacion y volvia a pedirsela al
  Investigador 3-4 veces de mas. Encontrado corriendo la demo real, no en
  teoria.
- **El Supervisor haciendo el calculo el mismo (y mal)**: en una corrida
  real, el Supervisor uso numeros que el Investigador habia agregado "de
  mas" en su resumen para escribir el promedio directamente, sin pasar por
  el Analista — y la conversion de unidades que hizo estaba mal (48h en
  vez de 16h). Fix: prompts mas estrictos en ambos nodos (el Investigador
  no debe convertir unidades: el Supervisor no debe calcular nada el
  mismo). Ver el detalle completo en
  [fase6_orquestador_multiagente/README.md](fase6_orquestador_multiagente/README.md#errores-comunes-evitados).
