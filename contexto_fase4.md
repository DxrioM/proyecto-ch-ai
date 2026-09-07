# Contexto de Proyecto — Fase 4: Escalabilidad documental (RAG avanzado y Pinecone)

> Continuacion de `contexto_fase1.md`, `contexto_fase2.md` y `contexto_fase3.md`. Este documento cubre unicamente la Fase 4 (Modulo 4 del curso "AI Engineering"): "Escalabilidad documental: RAG avanzado y Pinecone". Pensado para pegarlo como contexto en Claude Code una vez que las Fases 1-3 ya fueron aprobadas.

## 0. Relacion con las fases previas

- Fase 3 construyo un RAG **local**: ChromaDB en disco + embeddings locales + cadena LCEL de generacion grounded.
- Fase 4 escala esa misma logica a la **nube**: Pinecone Serverless reemplaza a ChromaDB como base vectorial, se agrega busqueda lexica (BM25) combinada con la semantica (busqueda hibrida), y se incorpora una capa de evaluacion cuantitativa (Precision@k / Recall@k). El chunking (`RecursiveCharacterTextSplitter`), el LLM de generacion (Groq/Gemini) y el patron de prompt "grounded" de la Fase 3 se reutilizan tal cual.

La Fase 4 tiene **cuatro componentes**: dos ejercicios de codigo + un repaso conceptual (flashcards) + la Pre-entrega 4 (entregable principal).

---

## 1. Objetivo de la Fase 4

Optimizar la escalabilidad y precision de sistemas de recuperacion utilizando Pinecone y tecnicas avanzadas de procesamiento documental:

- Configurar infraestructura vectorial en la nube (indices, namespaces, metadatos) con Pinecone Serverless.
- Disenar pipelines de ingesta masiva con batching y metadatos estructurados.
- Combinar busqueda semantica (vectorial) con busqueda lexica (BM25) en un **recuperador hibrido**.
- Medir cuantitativamente la calidad de la recuperacion con Precision@k y Recall@k.

---

## 2. Componente A — Ejercicio de codigo: "Pinecone Serverless: persistencia vectorial en la nube"

Automatizar la creacion de infraestructura Pinecone con el SDK de Python. Sin entregable formal separado, pero con rubrica propia.

### Enunciado (completar los TODO)

```python
import os
import asyncio
from pinecone import Pinecone, ServerlessSpec

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

async def setup_vector_infrastructure(index_name: str, dimension: int):
    """Configura la infraestructura de Pinecone Serverless y realiza una carga inicial."""
    # 1. Inicializar el cliente de Pinecone
    pc = None  # TODO

    # 2. Crear el indice si no existe
    # Tip: pc.list_indexes().names() para verificar existencia
    # Tip: ServerlessSpec para definir la nube (aws) y region (us-east-1)

    # 3. Conectar al indice
    index = None  # TODO

    # 4. Upsert de prueba usando un Namespace
    # Crea una lista de tuplas (id, vector, metadata)

    # 5. Retornar las estadisticas del indice usando describe_index_stats()
    return None

if __name__ == "__main__":
    asyncio.run(setup_vector_infrastructure("mi-indice-serverless", 1536))
```

### Solucion de referencia

```python
pc = Pinecone(api_key=PINECONE_API_KEY)

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=dimension,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
    while not pc.describe_index(index_name).status["ready"]:
        await asyncio.sleep(1)

index = pc.Index(index_name)

sample_vectors = [
    ("vec1", [0.1] * dimension, {"topic": "infraestructura", "priority": "high"}),
    ("vec2", [0.2] * dimension, {"topic": "seguridad", "priority": "medium"}),
]
index.upsert(vectors=sample_vectors, namespace="dev-environment")

stats = index.describe_index_stats()
return index
```

Nota: la dimension debe coincidir exactamente con el modelo de embeddings elegido — no tiene que ser 1536 obligatoriamente (ver seccion 7 para la opcion gratuita).

### Errores comunes a evitar

- **Mismatch de dimensiones**: insertar un vector de N dimensiones en un indice configurado para otra dimension distinta (falla inmediatamente).
- **Ignorar namespaces**: mezclar datos de prueba con produccion, o de distintos usuarios, en el mismo espacio logico.
- **Metrica erronea**: usar distancia euclidiana cuando el modelo de embeddings fue optimizado para similitud coseno.

### Rubrica (100 pts, aprobacion 65 pts)

| Criterio | Descripcion | Peso |
|---|---|---|
| Configuracion de infraestructura de indice | Correspondencia entre dimensiones, metrica de similitud y modelo de embeddings | 30% |
| Estrategia de namespaces y segmentacion | Organizar la informacion para multi-tenancy o separacion de entornos | 25% |
| Enriquecimiento con metadatos | Uso de metadatos en los vectores para filtrado estructurado | 25% |
| Eficiencia en la ingesta (upsert) | Implementacion tecnica del proceso de carga | 20% |

---

## 3. Componente B — Ejercicio de codigo: "Ingesta masiva y gestion de metadatos avanzados"

Pipeline de ingesta con batching y metadatos enriquecidos, sobre un mock de indice (no requiere cuenta real de Pinecone para resolverlo). Sin entregable formal separado, con rubrica propia.

### Enunciado (completar los TODO)

```python
import asyncio
import uuid
from datetime import datetime
from typing import List, Dict, Any

class MockPineconeIndex:
    async def upsert(self, vectors: List[Dict]):
        return {"upserted_count": len(vectors)}

    async def query(self, vector: List[float], top_k: int, filter: Dict = None):
        return {"matches": []}

class IngestionPipeline:
    def __init__(self, index: MockPineconeIndex):
        self.index = index

    def create_metadata(self, doc_text: str, category: str, author: str) -> Dict[str, Any]:
        """TODO: category, author, ingested_at (ISO format) y el tamano del texto."""
        pass

    async def process_and_upsert_batches(self, documents: List[Dict], batch_size: int = 100):
        """TODO: dividir en batches, preparar vectores (id, values, metadata), upsert por batch."""
        pass

    async def search_by_category(self, query_vector: List[float], category: str):
        """TODO: query con filtro de metadatos ($eq)."""
        pass
```

### Solucion de referencia

- `create_metadata`: `{"text": doc_text[:100], "category": category, "author": author, "ingested_at": datetime.utcnow().isoformat(), "char_count": len(doc_text)}` (guardar un snippet del texto original evita consultas adicionales a otra base de datos).
- `process_and_upsert_batches`: iterar la lista en trozos de `batch_size` (`for i in range(0, len(documents), batch_size)`), armar `{"id": str(uuid.uuid4()), "values": embedding, "metadata": self.create_metadata(...)}` por documento, y llamar `await self.index.upsert(vectors_to_upsert)` por cada batch, acumulando `upserted_count`.
- `search_by_category`: `await self.index.query(vector=query_vector, top_k=5, filter={"category": {"$eq": category}})`.

### Errores comunes a evitar

- **Schema drift**: no estandarizar los nombres de campos de metadatos (ej. `ingest_date` vs `date_created`) rompe los filtros.
- Batches demasiado grandes o insertar vector por vector (ineficiente); el punto dulce es 100-200 vectores por batch.
- No usar operadores de filtro (`$eq`, `$in`) para acotar el espacio de busqueda antes/durante la busqueda semantica.

### Rubrica (100 pts, aprobacion 65 pts)

| Criterio | Descripcion | Peso |
|---|---|---|
| Estrategia de batching y escalabilidad | Carga por lotes para optimizar latencia y estabilidad | 35% |
| Diseno y filtrado de metadatos | Estructurar y consultar metadatos para mejorar precision | 30% |
| Arquitectura y calidad de codigo | Legibilidad, mantenibilidad, robustez | 20% |
| Prevision de casos borde y seguridad | Concurrencia, limites de API, aislamiento de datos | 15% |

---

## 4. Componente C — Repaso conceptual: "Metricas y recuperacion hibrida" (flashcards)

No es un entregable, pero es la base teorica que la Pre-entrega 4 exige aplicar. Conceptos clave a tener presentes al implementar:

- **Precision vs Recall**: Precision = cuanto de lo recuperado es relevante (evita ruido); Recall = que proporcion de todo lo relevante fue encontrada (evita dejar informacion util afuera). Recall bajo → alucinaciones por falta de contexto; precision baja → ruido que confunde al LLM.
- **Por que combinar BM25 + embeddings**: BM25 (lexico, coincidencia exacta de terminos) es excelente para nombres propios, codigos de error o terminos tecnicos; los embeddings capturan significado conceptual y sinonimos. La busqueda hibrida combina ambos.
- **RRF (Reciprocal Rank Fusion)**: fusiona rankings de distintas fuentes (BM25 + vectorial) usando la *posicion* de cada documento, no sus puntuaciones absolutas — evita el error de sumar scores de escalas heterogeneas (un score BM25 de 20 no equivale a una similitud coseno de 0.8).
- **Re-ranking con cross-encoders**: segunda etapa que reordena con mayor precision el subconjunto (top-k) devuelto por el retrieval inicial; muy preciso pero lento, por eso se aplica solo a pocos candidatos, nunca a la busqueda completa.
- **Recall@k**: mide si al menos un documento relevante esta entre los primeros k resultados — la metrica clave para saber si el sistema "entrega el contexto necesario" al LLM.
- **F1-Score**: media armonica entre precision y recall, util para resumir el rendimiento en un solo numero.

`EnsembleRetriever` de LangChain (usado en la Pre-entrega 4) internamente resuelve la fusion de rankings de forma robusta (equivalente en espiritu a RRF), asi que no hace falta implementar RRF a mano salvo que se quiera ir mas alla del enunciado.

---

## 5. Componente D — Pre-entrega 4: "Sistema RAG escalable en la nube con Pinecone"

Este es el entregable principal de la Fase 4 (el que pediste incorporar literalmente).

### Que construir

Un **Modulo de Recuperacion Escalable** (servicio o conjunto de scripts organizados) que ejecute el flujo completo de un RAG en la nube:

1. **Pipeline de ingesta en Pinecone**: procesa documentos (PDF, Markdown o JSON) y los sube a un indice Pinecone Serverless con metadatos avanzados (fuente, pagina, categoria).
2. **Recuperador hibrido**: combina busqueda vectorial (Pinecone) con busqueda lexica (BM25) para mejorar precision en terminos tecnicos o nombres propios.
3. **Script de evaluacion**: calcula al menos Precision@k y Recall@k sobre un "Golden Set" de preguntas/respuestas de prueba.

### Pasos sugeridos

1. Preparar infraestructura: indice Serverless en Pinecone con la dimension que coincida con el modelo de embeddings elegido (ver seccion 7 para la opcion gratuita).
2. Ingesta inteligente: guardar el **texto original dentro de los metadatos** de Pinecone (evita consultas adicionales a otra base de datos relacional).
3. Configurar LangChain: `PineconeVectorStore` (paquete `langchain-pinecone`) o el SDK nativo de Pinecone como motor de busqueda vectorial.
4. Implementar BM25: `BM25Retriever` de LangChain (paquete `langchain_community`, requiere `rank_bm25`) + `EnsembleRetriever` para combinarlo con el retriever vectorial.
5. Evaluacion local: archivo JSON con pares `{"pregunta": "...", "documento_id_esperado": "..."}`; medir cuantos de esos documentos aparecen en el Top-5 recuperado.

### Implementacion sugerida (checklist tecnico del enunciado)

1. `.env` con `PINECONE_API_KEY`, `GROQ_API_KEY`/`GOOGLE_API_KEY` (o `OPENAI_API_KEY`/`ANTHROPIC_API_KEY` si se paga), e `INDEX_NAME`.
2. Script de setup que verifique si el indice existe (`pc.list_indexes().names()`) y lo cree si hace falta (Serverless), reutilizando el patron del Componente A.
3. Pipeline de ingesta:
   - Cargar un dataset de documentos tecnicos (ej. documentacion de una libreria de Python).
   - Chunking con `RecursiveCharacterTextSplitter` (punto medio recomendado: ~500-800 tokens, ni muy chico ni muy grande).
   - Generar embeddings e insertar en Pinecone incluyendo contenido y fuente en la metadata, en batches (Componente B).
4. Clase `RAGSystem` que encapsule un `EnsembleRetriever` (vectorial + BM25); recibe una consulta y devuelve los top-5 documentos combinando resultados lexicos y semanticos.
5. `evaluate.py`:
   - Benchmark de 5 preguntas con documento fuente conocido de antemano.
   - `Recall@5`: ¿esta el documento correcto entre los 5 recuperados?
   - `Precision@5`: ¿que porcentaje de los 5 recuperados son realmente utiles?
   - Imprimir en consola un resumen de resultados.

### Errores comunes a evitar

- **Mismatch de dimensiones**: subir embeddings de N dimensiones a un indice configurado con otra dimension.
- **Ignorar el namespace**: en escenarios multi-inquilino o con distintos tipos de datos, no usar `namespaces` degrada precision y velocidad.
- **Subestimar el chunking**: chunks muy chicos pierden contexto semantico; muy grandes diluyen la precision del embedding.

### Rubrica (100 pts, aprobacion 65 pts)

| Criterio | Descripcion | Peso |
|---|---|---|
| Configuracion e infraestructura cloud (Pinecone) | Inicializacion correcta del indice serverless + variables de entorno seguras | 15% |
| Pipeline de ingesta y gestion de metadatos | Procesar, fragmentar y persistir documentos tecnicos con metadatos utiles | 25% |
| Implementacion del recuperador hibrido | Clase `RAGSystem` con `EnsembleRetriever` combinando semantica + lexica | 35% |
| Evaluacion cuantitativa de metricas | `evaluate.py` calculando Recall@5 y Precision@5 sobre un benchmark | 25% |

### Que entregar (formato)

- Tipo: **repositorio de GitHub**.
- Artefactos concretos: pipeline de ingesta a Pinecone, recuperador hibrido (BM25 + vectorial), `evaluate.py` (Precision@k y Recall@k).
- El `README.md` debe incluir los pasos para **replicar el indice** de Pinecone.
- **No hace falta PDF**: el reporte de metricas se imprime en consola y se resume en el README.

---

## 6. Requisitos transversales (heredados de fases previas)

1. **Python 3.12+**, asincronia real donde aplique (la ingesta y las consultas pueden ser `async def`, siguiendo el patron de fases anteriores).
2. **Codigo en ingles**; **texto de cara al usuario en español sin tildes ni "ñ"** (logs, mensajes, reportes de consola).
3. `.env` / `.env.example` / `.gitignore` actualizados — nunca commitear `PINECONE_API_KEY` ni ninguna otra key.
4. **Preferir componentes gratuitos** en toda la pila (ver seccion 7).
5. `top_k` acotado (recomendado 5) tanto en el retriever hibrido como en la evaluacion.

---

## 7. Estrategia de gratuidad para esta fase (Pinecone + embeddings + BM25 + LLM)

| Pieza | Opcion recomendada | Costo | Notas |
|---|---|---|---|
| Base vectorial cloud | **Pinecone Starter (free tier)** | Gratis, sin tarjeta | Hasta 5 indices, 100 namespaces, 2 GB de storage, 2M write units/mes y 1M read units/mes. Mas que suficiente para este ejercicio. Crear cuenta en `app.pinecone.io`. |
| Embeddings | **Modelo local gratuito** (ej. `sentence-transformers/all-MiniLM-L6-v2`, 384 dimensiones) via `langchain_huggingface.HuggingFaceEmbeddings`, igual que en la Fase 3 | Gratis, sin API key | El enunciado menciona 1536 solo como ejemplo si se usa `text-embedding-3-small` de OpenAI (pago). **La dimension del indice de Pinecone debe crearse igual a la del modelo elegido** (ej. 384), no es obligatorio usar 1536. |
| Busqueda lexica (BM25) | `langchain_community.retrievers.BM25Retriever` + libreria `rank_bm25` | Gratis, corre local, sin API | No depende de ningun proveedor externo. |
| LLM (generacion final) | **Groq** (`ChatGroq`) o **Gemini** (`ChatGoogleGenerativeAI`) — igual que en fases 2 y 3 | Gratis, sin tarjeta | Reutilizar las keys ya configuradas en `.env`. |

**Importante**: si mas adelante se decide usar `OpenAIEmbeddings` de pago, el indice de Pinecone debe crearse con `dimension=1536` (o la que corresponda al modelo) y usarse ese mismo embedding tanto para indexar como para consultar — el mismatch de dimensiones/embeddings es, otra vez, el error #1 mencionado en el enunciado.

---

## 8. Estructura de proyecto sugerida (extension de fases anteriores)

```
proyecto_ch_ai/
├── .env
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── entregable_a_orquestador/        # Fase 1
├── entregable_b_llm_client/         # Fase 1
├── fase2_lcel_refactor/             # Fase 2
├── fase2_ejercicio_validacion/      # Fase 2
├── fase2_pipeline_validado/         # Fase 2
├── fase3_ejercicio_chunking/        # Fase 3
├── fase3_ejercicio_chromadb/        # Fase 3
├── fase3_rag_local/                 # Fase 3
├── fase4_ejercicio_pinecone_setup/
│   └── setup_infra.py               # Componente A
├── fase4_ejercicio_ingesta_masiva/
│   └── ingestion_pipeline.py        # Componente B
└── fase4_rag_pinecone/               # Componente D: Pre-entrega 4 (entregable principal)
    ├── data/                        # dataset de documentos tecnicos
    ├── golden_set.json              # preguntas + documento_id_esperado
    ├── setup_index.py               # crea/verifica el indice Serverless
    ├── ingest.py                    # chunking + embeddings + upsert con metadata
    ├── rag_system.py                # clase RAGSystem (EnsembleRetriever: Pinecone + BM25)
    ├── evaluate.py                  # Precision@5 / Recall@5 sobre el golden set
    └── README.md                    # incluye pasos para replicar el indice
```

---

## 9. Checklist final antes de dar la Fase 4 por aprobada

- [ ] Componente A: `setup_vector_infrastructure` crea el indice Serverless solo si no existe, con dimension y metrica correctas, y hace un upsert de prueba con namespace.
- [ ] Componente B: `IngestionPipeline` procesa documentos en batches, genera metadatos enriquecidos (`ingested_at`, `category`, `author`, etc.) y permite busqueda filtrada por categoria.
- [ ] Componente D (Pre-entrega 4): indice Pinecone creado/verificado, ingesta con chunking (~500-800 tokens) y metadata (incluyendo texto original + fuente), `RAGSystem` con `EnsembleRetriever` (Pinecone + BM25) devolviendo top-5.
- [ ] `evaluate.py` calcula Precision@5 y Recall@5 sobre un golden set de al menos 5 preguntas, e imprime el resumen en consola.
- [ ] Dimension del indice coincide exactamente con el modelo de embeddings usado (recomendado: modelo local gratuito, ej. 384 dims).
- [ ] Namespaces usados correctamente si hay mas de un tipo de dato/entorno.
- [ ] `.env` / `.env.example` / `.gitignore` sin ninguna API key expuesta.
- [ ] `README.md` con instrucciones para replicar el indice de Pinecone (no hace falta PDF).
- [ ] Codigo en ingles; mensajes al usuario en español sin tildes/ñ.
