# Sistema RAG Escalable en la Nube con Pinecone — Pre-entrega 4

Escala el RAG local de la Fase 3 a la nube: Pinecone Serverless reemplaza a
ChromaDB, se agrega recuperacion hibrida (vectorial + BM25) y una capa de
evaluacion cuantitativa (`Precision@5` / `Recall@5`).

## Estado de este componente

**Validado end-to-end contra Pinecone real** (indice `proyecto-ch-ai-fase4`,
free tier). Resultado de `evaluate.py` sobre el golden set de 5 preguntas:

```
Recall@5: 1.00
Precision@5: 0.25
```

- **Recall@5 = 1.00**: el documento fuente correcto aparecio entre los
  recuperados en las 5 preguntas, y en los 5 casos quedo **primero** en el
  ranking — la busqueda hibrida (Pinecone + BM25) funciona.
- **Precision@5 = 0.25 es un artefacto del tamano del corpus de prueba**,
  no un problema de calidad: el dataset de ejemplo tiene solo 4 documentos
  en total, asi que pedir `top_k=5` siempre devuelve los 4 (1 correcto de
  4 recuperados = 0.25) en vez de filtrar ruido real. Con un corpus mas
  grande (docenas o cientos de documentos), `Precision@5` reflejaria
  cuanto ruido hay entre los 5 recuperados de verdad.

Dos bugs reales se encontraron y corrigieron durante esta validacion (no
detectables sin conexion real a Pinecone):

1. `LocalChromaEmbeddings` devolvia `numpy.float32` en vez de `float`
   nativo de Python — el SDK de Pinecone no puede serializar eso a JSON
   (`upsert` fallaba con `PineconeTypeError`).
2. `IngestionPipeline.create_metadata()` (Componente B) no tiene un campo
   `source`, solo `category` — sin el, no habia forma de saber de que
   archivo vino cada chunk recuperado. Se agrego `extra_metadata`
   inyectable (opcional, no rompe el comportamiento del Componente B) para
   poder incluir `source` sin tocar el esquema generico del ejercicio.

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

## Que esta probado

- Tests sinteticos (sin red, deterministas): `LocalChromaEmbeddings`
  (dimension 384), `PineconeRetriever` con un indice falso,
  `evaluate.evaluar()` con sistemas falsos (perfecto / siempre falla), e
  idempotencia + limpieza de chunks huerfanos de `ingest()` — ver
  `tests/test_fase4_resilience.py`.
- Validacion real end-to-end (ver "Estado de este componente" arriba):
  `setup_infra.py` crea el indice real e idempotente (2da corrida lo
  reutiliza sin recrearlo), `ingest.py` sube el corpus completo, y
  `evaluate.py` da `Recall@5 = 1.00` sobre el golden set.

## Variables de entorno

Ademas de `GROQ_API_KEY`/`GOOGLE_API_KEY` (heredadas de fases anteriores,
no se usan en este componente ya que solo cubre retrieval, no generacion),
este componente necesita:

| Variable | Notas |
|---|---|
| `PINECONE_API_KEY` | Gratis, sin tarjeta — `app.pinecone.io` |
