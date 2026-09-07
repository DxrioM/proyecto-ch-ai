# Sistema RAG Escalable en la Nube con Pinecone — Pre-entrega 4

Escala el RAG local de la Fase 3 a la nube: Pinecone Serverless reemplaza a
ChromaDB, se agrega recuperacion hibrida (vectorial + BM25) y una capa de
evaluacion cuantitativa (`Precision@5` / `Recall@5`).

## Estado de este componente

> **Pendiente de validacion end-to-end real**: este componente necesita
> una cuenta de Pinecone (`PINECONE_API_KEY`, free tier, sin tarjeta —
> `app.pinecone.io`). El codigo esta completo y las partes que no dependen
> de una conexion real a Pinecone ya estan probadas (ver "Que esta
> validado" mas abajo); en cuanto la key este disponible, correr
> `python -m fase4_rag_pinecone.ingest` seguido de
> `python -m fase4_rag_pinecone.evaluate` y actualizar esta seccion con los
> resultados reales.

## Como replicar el indice de Pinecone

1. Crear una cuenta gratuita en `app.pinecone.io` (no pide tarjeta).
2. Generar un API key y agregarlo como `PINECONE_API_KEY` en el `.env` de
   la raiz del proyecto.
3. Correr la ingesta — crea el indice Serverless si no existe (idempotente,
   reutiliza `ensure_index_exists` del Componente A) y sube el corpus:

   ```bash
   python -m fase4_rag_pinecone.ingest
   ```

   Esto crea el indice `proyecto-ch-ai-fase4` (region `aws`/`us-east-1`,
   metrica `cosine`, dimension `384`) y sube los chunks al namespace
   `fase4-corpus`. No hace falta ningun paso manual en la consola de
   Pinecone.

4. Evaluar la calidad de la recuperacion:

   ```bash
   python -m fase4_rag_pinecone.evaluate
   ```

## Arquitectura

- `embeddings.py`: `LocalChromaEmbeddings`, adaptador LangChain sobre el
  mismo modelo local de la Fase 3 (Sentence Transformers all-MiniLM-L6-v2
  via ONNX, 384 dimensiones, sin API key). **Nota de compatibilidad**:
  `langchain-pinecone` (el paquete "oficial" que sugiere la consigna)
  todavia no tiene build para Python 3.14 en este entorno (depende de
  `simsimd<4.0`, sin wheels para 3.14) — en vez de instalar
  `sentence-transformers`/`torch` de nuevo para usarlo, se reutiliza el
  mismo embedding ya cacheado de la Fase 3.
- `pinecone_retriever.py`: `PineconeRetriever`, un `BaseRetriever` de
  LangChain propio sobre el SDK nativo de `pinecone` (sustituye a
  `PineconeVectorStore` por la misma razon de compatibilidad). Cumple el
  mismo contrato, asi que se combina con `BM25Retriever` exactamente igual
  que si se hubiera usado el paquete oficial.
- `ingest.py`: reutiliza `DocumentProcessor` (Fase 3, chunking por tokens,
  600/100 en vez de 500/50 — dentro del rango 500-800 que pide esta fase),
  `ensure_index_exists` (Componente A) e `IngestionPipeline` (Componente
  B, con IDs deterministicos en vez de `uuid4` para poder ser idempotente,
  y guardando el texto **completo** en la metadata en vez del snippet de
  100 caracteres del ejercicio generico). Guarda un `manifest.json` (hash
  por archivo) y un `chunks_cache.json` (para que `rag_system.py` arme el
  lado BM25 sin releer los archivos fuente).
- `rag_system.py`: `RAGSystem` — `EnsembleRetriever` (pesos 50/50) que
  combina `PineconeRetriever` (semantico) con `BM25Retriever` (lexico,
  local, sobre el `chunks_cache.json`).
- `evaluate.py`: `Recall@5` (¿esta el documento esperado entre los 5
  recuperados?) y `Precision@5` (¿que fraccion de los 5 recuperados son del
  documento esperado?) sobre `golden_set.json` (5 preguntas con fuente
  conocida).

## Que esta validado ahora mismo (sin Pinecone real)

- `LocalChromaEmbeddings`: dimension real verificada en 384, coincide con
  el indice configurado.
- `PineconeRetriever`: probado con un indice falso (misma forma de
  respuesta que el SDK real) — arma correctamente los `Document` de
  LangChain a partir de los matches.
- `evaluate.evaluar()`: probado con sistemas falsos (uno que siempre
  acierta, uno que siempre falla) — la logica de `Recall@k`/`Precision@k`
  da los numeros esperados en ambos casos extremos.
- Componente A (`setup_infra.py`) y Componente B (`ingestion_pipeline.py`)
  validados por separado (ver sus propias secciones en el README raiz).

Lo unico que falta ejercitar con una cuenta real es la ingesta y
recuperacion contra Pinecone en si (network + indice real).

## Variables de entorno

Ademas de `GROQ_API_KEY`/`GOOGLE_API_KEY` (heredadas de fases anteriores,
no se usan en este componente ya que solo cubre retrieval, no generacion),
este componente necesita:

| Variable | Notas |
|---|---|
| `PINECONE_API_KEY` | Gratis, sin tarjeta — `app.pinecone.io` |
