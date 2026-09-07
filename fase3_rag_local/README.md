# Sistema de Recuperacion Semantica Local (RAG) — Pre-entrega 3

Sistema RAG end-to-end: ingesta documentos locales, los indexa en ChromaDB
con embeddings 100% locales (sin API key), y responde preguntas
**exclusivamente** en base a lo que encuentra en esos documentos — si la
respuesta no esta en el contexto recuperado, dice que no la tiene, en vez
de inventarla.

## Dataset de ejemplo

`data/` contiene 4 documentos markdown sobre un "Sistema de Pedidos
Online" ficticio (arquitectura, despliegue, troubleshooting, politicas de
soporte) — suficiente variedad tematica para poder distinguir una pregunta
respondible de una pregunta trampa.

## Arquitectura

- `ingest.py`: lee `data/*.md`, los fragmenta con
  [`fase3_ejercicio_chunking.DocumentProcessor`](../fase3_ejercicio_chunking/document_processor.py)
  (chunking por tokens con `tiktoken` + `RecursiveCharacterTextSplitter`) y
  los persiste con
  [`fase3_ejercicio_chromadb.VectorMemoryManager`](../fase3_ejercicio_chromadb/vector_memory_manager.py).
  **Idempotente**: guarda un hash de cada archivo en
  `vectorstore/manifest.json`; si un archivo no cambio, no se vuelve a
  fragmentar ni a re-embeder en la proxima corrida.
- `rag_chain.py`: define `RagResponse` (Pydantic: `respuesta`, `fuentes`,
  `encontrado_en_contexto`), el prompt "filtro de veracidad", y
  `get_rag_response(query, manager)` — recupera los `top_k` (4) fragmentos
  mas relevantes de ChromaDB, arma el contexto citando la fuente de cada
  fragmento, y genera la respuesta con la cadena LCEL de la Fase 2
  (`prompt | model.with_structured_output(RagResponse).with_retry()`).
- `main.py`: corre la ingesta y dos pruebas obligatorias — una pregunta
  respondible y una pregunta trampa.

## Uso

Requiere `GROQ_API_KEY` en el `.env` de la raiz del proyecto.

```bash
python -m fase3_rag_local.main
```

## Pruebas obligatorias (evidencia real, corrida contra Groq)

**Pregunta respondible**: *"Que base de datos usa el sistema de pedidos
para persistencia?"*

```json
{
  "respuesta": "El sistema de pedidos persiste sus datos en PostgreSQL 16.",
  "fuentes": ["arquitectura.md"],
  "encontrado_en_contexto": true
}
```

**Pregunta trampa** (no esta en ningun documento): *"Cual es la politica de
reembolsos para clientes VIP en compras internacionales?"*

```json
{
  "respuesta": "No tengo esa informacion en la base de conocimiento proporcionada.",
  "fuentes": [],
  "encontrado_en_contexto": false
}
```

El sistema no alucino: reconocio correctamente que la politica de
reembolsos no esta documentada y lo dijo explicitamente, en vez de
inventar una respuesta plausible.

## Decisiones clave (evitar los errores comunes de la consigna)

- **Mismo modelo de embeddings para indexar y consultar**:
  `VectorMemoryManager` usa `embedding_functions.DefaultEmbeddingFunction()`
  de Chroma (Sentence Transformers `all-MiniLM-L6-v2` via ONNX, local, sin
  API key) una unica vez al crear la coleccion; Chroma la reutiliza
  automaticamente en cada `query()`, asi que es fisicamente imposible que
  se desincronice.
- **`top_k` acotado a 4** (entre 3 y 5): evita pasarle "contexto infinito"
  al LLM.
- **Idempotencia real**: `ingest.py` no solo evita reprocesar archivos sin
  cambios — si un archivo cambia y genera *menos* chunks que antes, borra
  los IDs viejos que sobran (`delete_by_id`) para no dejar chunks huerfanos
  con contenido desactualizado en la coleccion.
- **IDs deterministicos**: `f"{nombre_archivo}_{indice_de_chunk}"`, nunca
  aleatorios — permite que `upsert()` actualice en vez de duplicar.

## Vectorstore local

`vectorstore/` (la base de ChromaDB en disco + `manifest.json`) se genera
la primera vez que se corre `ingest()` y **no se versiona** (ver
`.gitignore`): cualquiera que clone el repo la regenera corriendo
`python -m fase3_rag_local.main`.
