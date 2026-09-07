# Contexto de Proyecto — Fase 3: Persistencia de datos y vector DBs

> Continuacion de `contexto_fase1.md` y `contexto_fase2.md`. Este documento cubre unicamente la Fase 3 (Modulo 3 del curso "AI Engineering"): "Persistencia de datos y vector DBs". Pensado para pegarlo como contexto en Claude Code una vez que las Fases 1 y 2 ya fueron aprobadas.

## 0. Relacion con las fases previas

- Fase 1 dio el cliente async de LLM (`AsyncLLMManager`).
- Fase 2 dio la orquestacion declarativa con LangChain/LCEL (`prompt | model | parser`, `with_structured_output`, `with_retry`).
- Fase 3 agrega la pieza de **memoria de largo plazo**: convertir texto en vectores (embeddings), guardarlos en una base vectorial local (ChromaDB) y usarlos para recuperar contexto relevante antes de generar una respuesta (RAG = Retrieval-Augmented Generation). El LLM y la cadena LCEL de la Fase 2 se reutilizan tal cual para la etapa de generacion.

La Fase 3 tiene **cuatro componentes evaluables**: tres ejercicios de unidad + una pre-entrega.

---

## 1. Objetivo de la Fase 3

Implementar un sistema de memoria de largo plazo mediante arquitecturas RAG basicas y bases de datos vectoriales locales:

- Entender embeddings y metricas de similitud (coseno, euclidea, producto punto).
- Fragmentar (chunking) documentos de forma que preserve el significado.
- Persistir y consultar vectores en ChromaDB local (CRUD).
- Ensamblar un flujo RAG end-to-end: ingesta → recuperacion → generacion "grounded" (basada solo en el contexto recuperado).

---

## 2. Componente A — Ejercicio: "Embeddings y Similitud: La Geometria del Lenguaje"

Ejercicio teorico-practico, sin codigo de produccion obligatorio (aunque incluye fragmentos de codigo/pseudocodigo).

### Consigna

1. Seleccionar 5 oraciones que traten el mismo concepto tecnico (ej. "Despliegue de microservicios") con vocabulario totalmente distinto entre si (sinonimia, sin repetir palabras clave).
2. Incluir 2 oraciones "trampa" que compartan palabras clave pero tengan significado opuesto o irrelevante (ej. "El servicio de micro-limpieza es excelente").
3. Investigar como calcular la Similitud Coseno entre dos vectores con `scikit-learn` (codigo o pseudocodigo).
4. Diseñar un diagrama de flujo simple de un proceso de busqueda semantica: desde que el usuario ingresa una query hasta que el sistema devuelve el documento mas parecido.

### Rubrica (100 pts, aprobacion 65 pts)

| Criterio | Descripcion | Peso |
|---|---|---|
| Seleccion y analisis semantico | Ejemplos que desafien la tecnica (sinonimia vs. trampas de palabras clave) | 30% |
| Implementacion de similitud coseno | Uso correcto de librerias estandar de Python para el calculo de distancias/similitud | 35% |
| Arquitectura del flujo de busqueda | Diseño logico del pipeline texto → vector → busqueda semantica | 25% |
| Claridad y calidad del entregable | Presentacion tecnica, redaccion, formato | 10% |

### Entregable

- Tipo: **archivo (PDF)**. Debe incluir: el analisis de las 7 oraciones (5 + 2 trampa), el fragmento de codigo/pseudocodigo de similitud coseno, y el diagrama de flujo.

---

## 3. Componente B — Ejercicio de codigo: "Estrategias de Chunking y preprocesamiento de documentos"

Ejercicio de unidad centrado en `RecursiveCharacterTextSplitter` + limpieza de texto + medicion por tokens (no caracteres). Sin tipo de entregable formal separado en el temario, pero con rubrica propia — resolver dentro del repo de la Fase 3.

### Enunciado (completar los TODO)

```python
import re
import tiktoken
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentProcessor:
    def __init__(self, model_encoding: str = "cl100k_base"):
        # TODO: Inicializar el encoding de tiktoken
        self.tokenizer = None
        # TODO: Configurar RecursiveCharacterTextSplitter
        # Debe usar una funcion personalizada para medir longitud por TOKENS, no caracteres.
        self.splitter = None

    def clean_text(self, text: str) -> str:
        """Limpia el texto eliminando espacios duplicados y saltos de linea innecesarios."""
        return text

    def calculate_tokens(self, text: str) -> int:
        """Calcula la cantidad de tokens usando el tokenizer de tiktoken."""
        return 0

    def process_document(self, raw_text: str) -> List[str]:
        """Pipeline: Limpieza -> Fragmentacion."""
        return []

if __name__ == "__main__":
    text = "Tu texto largo aqui..."
    processor = DocumentProcessor()
    chunks = processor.process_document(text)
    print(f"Chunks generados: {len(chunks)}")
```

### Solucion de referencia

- `self.tokenizer = tiktoken.get_encoding(model_encoding)` (usar `"cl100k_base"` para modelos estilo GPT-4; si se usa otro proveedor, elegir el encoding equivalente mas cercano o documentar la aproximacion).
- `self.splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50, length_function=self.calculate_tokens, separators=["\n\n", "\n", ".", " ", ""])`.
- `clean_text`: `re.sub(r'\s+', ' ', text)` para normalizar espacios/saltos de linea, mas limpieza de puntuacion repetida (`re.sub(r'(\.\s){2,}', '. ', text)`), y `.strip()` final.
- `calculate_tokens`: `len(self.tokenizer.encode(text))`.
- `process_document`: limpiar → `self.splitter.split_text(cleaned_text)` → loguear la cantidad de tokens por chunk generado.

### Errores comunes a evitar

- Chunks demasiado pequeños: pierden contexto global.
- Medir tamaño en caracteres en vez de tokens (usar siempre `tiktoken` u otro tokenizador real).
- No limpiar el texto antes de fragmentar ("basura entra, basura sale").

### Rubrica (100 pts, aprobacion 65 pts)

| Criterio | Descripcion | Peso |
|---|---|---|
| Calidad del preprocesamiento y limpieza | Eliminar ruido (encabezados, saltos de linea excesivos, caracteres basura) | 25% |
| Logica de segmentacion (chunking) | Division priorizando coherencia semantica sobre el corte arbitrario | 35% |
| Gestion de contexto y overlap | Uso de solapamiento para preservar conceptos en los bordes | 25% |
| Practicas de ingenieria de IA | Tokenizadores vs. caracteres, legibilidad del codigo | 15% |

---

## 4. Componente C — Ejercicio de codigo: "Persistencia local con ChromaDB: operaciones CRUD"

Ejercicio de unidad centrado en encapsular ChromaDB en una clase robusta. Sin entregable formal separado, con rubrica propia.

### Enunciado (completar los TODO)

```python
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any

class VectorMemoryManager:
    def __init__(self, persist_path: str, collection_name: str):
        # TODO: Inicializar el PersistentClient de ChromaDB con la ruta dada
        self.client = None
        # TODO: Crear u obtener la coleccion usando self.client.get_or_create_collection
        # No olvides asignar una funcion de embedding por defecto
        self.collection = None

    def upsert_documents(self, ids: List[str], documents: List[str], metadatas: List[Dict[str, Any]]):
        """Implementa el metodo upsert para evitar errores por IDs duplicados."""
        pass

    def semantic_search(self, query_text: str, n_results: int = 3):
        """Realiza una busqueda por similitud. Retorna los documentos mas cercanos al query_text."""
        pass
```

### Solucion de referencia

- `self.client = chromadb.PersistentClient(path=persist_path)` (persistencia real en disco, nunca cliente en memoria).
- `self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()` (Sentence Transformers local, gratis, sin API key — ver seccion 7).
- `self.collection = self.client.get_or_create_collection(name=collection_name, embedding_function=self.embedding_fn)`.
- `upsert_documents`: `self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas)` dentro de un `try/except` que loguee errores especificos.
- `semantic_search`: `self.collection.query(query_texts=[query_text], n_results=n_results, include=["documents", "metadatas", "distances"])`, formateando la salida a una lista de dicts `{id, document, metadata, distance}`.
- `delete_by_id`: `self.collection.delete(ids=ids)`.

### Errores comunes a evitar

- IDs no deterministicos (usar hashes del contenido o IDs estructurados en vez de IDs aleatorios).
- Desajuste de embeddings entre indexado y consulta.
- No inicializar el cliente con una ruta de disco (perdida de datos al cerrar el script).
- Usar `add()` en vez de `upsert()` para ingestas incrementales (`add` falla si el ID ya existe).

### Rubrica (100 pts, aprobacion 65 pts)

| Criterio | Descripcion | Peso |
|---|---|---|
| Implementacion del cliente y persistencia | Inicializacion correcta de ChromaDB con almacenamiento en disco y gestion de la coleccion | 25% |
| Operaciones CRUD y estrategia de IDs | Insertar, consultar, actualizar y eliminar vectores de forma deterministica | 35% |
| Gestion de metadatos y filtrado | Uso de metadatos para enriquecer la busqueda y permitir filtrado selectivo | 20% |
| Calidad del codigo y manejo de errores | Limpieza del codigo, tipado, captura de excepciones especificas de la base de datos | 20% |

---

## 5. Componente D — Pre-entrega 3: "Sistema de recuperacion semantica local (RAG)"

Este es el entregable principal de la Fase 3 (el que pediste incorporar literalmente).

### Que construir

Un script o notebook Python con un flujo **End-to-End de RAG**: recibe una consulta, busca informacion relevante en una base vectorial previamente poblada, y genera una respuesta que usa **exclusivamente** esa informacion.

Componentes requeridos:

1. **Modulo de ingesta (setup)**: funcion que tome documentos `.txt`/`.md`, los fragmente (chunking) y los persista en una coleccion de ChromaDB.
2. **Capa de recuperacion (retriever)**: logica que convierta la pregunta del usuario en embedding y recupere los fragmentos mas relevantes.
3. **Generacion grounded**: cadena LCEL (Fase 2) que recibe los documentos recuperados + la pregunta y genera una respuesta. El prompt debe instruir al modelo a decir "No lo se" si la respuesta no esta en el contexto.

### Pasos sugeridos

1. Elegir 3-4 archivos de texto sobre un tema especifico (manuales tecnicos, apuntes, normativas). Aplicar el `RecursiveCharacterTextSplitter` del Componente B.
2. Inicializar ChromaDB con `PersistentClient` en una carpeta local (ej. `./vectorstore`). **Usar el mismo modelo de embeddings para indexar y para consultar** (ver seccion 7 — critico).
3. Diseñar un prompt de sistema como "filtro de veracidad": *"Eres un asistente tecnico. Responde solo basandote en el CONTEXTO proporcionado. Si la respuesta no esta alli, di que no tienes acceso a esa informacion."*
4. Construir la cadena LCEL: retriever + transformador de documentos + modelo de lenguaje; el output pasa por un `PydanticOutputParser` (o `with_structured_output`, siguiendo el patron de la Fase 2) que incluya el texto de la respuesta y las referencias/fuentes usadas.

### Implementacion sugerida (checklist tecnico del enunciado)

1. Entorno virtual con `langchain`, `chromadb`, el SDK del proveedor elegido (ver seccion 7) y `pydantic`.
2. Script de carga: lee archivos de una carpeta `/data`, aplica chunking (minimo 500 tokens, 50 de overlap), los guarda en ChromaDB local. **Debe verificar si la coleccion ya existe antes de reindexar todo** (idempotencia).
3. Funcion asincrona `get_rag_response(query: str)` que:
   a. Hace busqueda de similitud en ChromaDB (`top_k` entre 3 y 5, nunca mas — evitar "contexto infinito" / "Lost in the Middle").
   b. Construye el prompt incluyendo los fragmentos recuperados.
   c. Llama al LLM de forma asincrona.
   d. Parsea la respuesta a un modelo Pydantic que incluya el texto y las referencias/fuentes.
4. Dos pruebas obligatorias: una pregunta cuya respuesta este en los documentos, y una "pregunta trampa" cuya respuesta no este — verificar que el modelo no alucine y responda algo equivalente a "no lo se".
5. No incluir API keys en el codigo (usar `.env`).

### Errores comunes a evitar

- **"Contexto infinito"**: no pasar decenas de fragmentos al LLM; mantener `top_k` entre 3 y 5.
- **Embeddings no coincidentes**: indexar con un modelo de embeddings y consultar con otro distinto invalida completamente la busqueda (es el error #1 segun la catedra).
- **Falta de persistencia/idempotencia**: el script debe verificar si la base ya existe antes de reindexar todo desde cero.

### Ejemplo de estructura de respuesta (Pydantic, sugerido)

```python
class RagResponse(BaseModel):
    respuesta: str
    fuentes: list[str]   # ids o nombres de archivo de los chunks usados
    encontrado_en_contexto: bool
```

### Rubrica (100 pts, aprobacion 65 pts)

| Criterio | Descripcion | Peso |
|---|---|---|
| Estrategia de chunking e ingesta | Procesar `/data` aplicando fragmentacion que preserve el contexto semantico | 25% |
| Arquitectura asincrona y recuperacion | `get_rag_response` con patrones asincronos para la consulta y el LLM | 35% |
| Validacion con Pydantic y esquemas | Salida estructurada que contenga las fuentes | 20% |
| Robustez y evidencia de pruebas | Comportamiento correcto ante preguntas fuera de contexto + credenciales seguras | 20% |

### Que entregar (formato)

- Tipo: **repositorio de GitHub**.
- Artefactos concretos: script de ingesta (chunking + ChromaDB), script/notebook con la cadena RAG asincrona, un dataset de ejemplo (`.txt`/`.md`), y `README.md`.
- **No hace falta documento de analisis**: el `README.md` alcanza como documentacion.

---

## 6. Requisitos transversales (heredados de fases previas + especificos de RAG)

1. **Python 3.12+**, asincronia real en la capa de generacion (`get_rag_response` como `async def`, `ainvoke` en la cadena LCEL).
2. **Codigo en ingles**; **texto de cara al usuario en español sin tildes ni "ñ"**.
3. `.env` / `.env.example` / `.gitignore` actualizados (nunca subir API keys).
4. **Preferir componentes gratuitos** en toda la pila: embeddings locales + LLM gratis via Groq/Gemini (ver seccion 7).
5. El prompt de generacion siempre debe permitir explicitamente la respuesta "no lo se" — nunca alucinar fuera del contexto recuperado.
6. `top_k` acotado (3-5) en toda busqueda de similitud.

---

## 7. Estrategia de gratuidad para esta fase (embeddings + vector DB + LLM)

| Pieza | Opcion recomendada | Costo | Notas |
|---|---|---|---|
| Base vectorial | **ChromaDB** en modo `PersistentClient` (local, en disco) | Gratis, sin cuenta ni API key | Ya lo pide el enunciado. No requiere Docker. |
| Embeddings | **`embedding_functions.DefaultEmbeddingFunction()`** de Chroma (Sentence Transformers, ej. `all-MiniLM-L6-v2`) corriendo 100% local | Gratis, sin API key | Elimina de raiz el error #1 ("embeddings no coincidentes"): al no depender de ninguna API externa, el mismo modelo se usa siempre para indexar y consultar. Alternativa equivalente si se prefiere el ecosistema LangChain: `langchain_huggingface.HuggingFaceEmbeddings` con el mismo modelo. |
| LLM (generacion) | **Groq** (`ChatGroq`) o **Gemini** (`ChatGoogleGenerativeAI`) — igual que en la Fase 2 | Gratis, sin tarjeta | Reutilizar las mismas keys (`GROQ_API_KEY` / `GOOGLE_API_KEY`) ya configuradas en `.env` desde la Fase 1. |

**Importante**: si en algun punto se decide usar `OpenAIEmbeddings` (de pago) para los vectores, hay que usar ese mismo embedding tanto para indexar como para consultar — nunca mezclar con el `DefaultEmbeddingFunction` local. La recomendacion por defecto de este documento evita el problema directamente al no usar ningun embedding pago.

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
├── fase3_ejercicio_chunking/
│   └── document_processor.py        # Componente B
├── fase3_ejercicio_chromadb/
│   └── vector_memory_manager.py     # Componente C
└── fase3_rag_local/                 # Componente D: Pre-entrega 3 (entregable principal)
    ├── data/                        # dataset de ejemplo (.txt/.md)
    ├── ingest.py                    # modulo de ingesta: chunking + persistencia en ChromaDB
    ├── rag_chain.py                 # retriever + cadena LCEL de generacion grounded
    ├── main.py                      # get_rag_response(query) + pruebas (pregunta valida + trampa)
    ├── vectorstore/                 # carpeta persistente de ChromaDB (NO versionar datos grandes)
    └── README.md
```

Nota: el analisis de embeddings/similitud (Componente A) es un PDF, no requiere codigo dentro del repo, pero puede documentarse tambien en una carpeta `fase3_embeddings_similitud/` con el PDF y el script de apoyo si se quiere mantener todo centralizado.

---

## 9. Checklist final antes de dar la Fase 3 por aprobada

- [ ] Componente A: PDF con 5 oraciones semanticamente equivalentes + 2 trampa, calculo de similitud coseno (codigo o pseudocodigo con `scikit-learn`), diagrama de flujo de busqueda semantica.
- [ ] Componente B: `DocumentProcessor` con limpieza por regex, `RecursiveCharacterTextSplitter` midiendo por tokens (`tiktoken`), chunk_size=500/overlap=50.
- [ ] Componente C: `VectorMemoryManager` con `PersistentClient`, `get_or_create_collection`, `upsert`, `semantic_search` (con `include=["documents","metadatas","distances"]`), `delete_by_id`, IDs deterministicos.
- [ ] Componente D (Pre-entrega 3): ingesta desde `/data` con verificacion de idempotencia, `get_rag_response()` asincrona con `top_k` 3-5, prompt "filtro de veracidad", salida validada con Pydantic incluyendo fuentes.
- [ ] Mismo modelo de embeddings usado para indexar y para consultar (recomendado: `DefaultEmbeddingFunction` local, gratis).
- [ ] Dos pruebas documentadas: pregunta respondible + pregunta trampa (el sistema no debe alucinar).
- [ ] `.env` / `.env.example` / `.gitignore` sin API keys expuestas.
- [ ] `README.md` explicando como ejecutar el sistema (sin necesidad de PDF adicional).
- [ ] Codigo en ingles; mensajes al usuario en español sin tildes/ñ.
