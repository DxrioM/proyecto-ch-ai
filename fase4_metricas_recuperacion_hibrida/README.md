# Componente C — Metricas y recuperacion hibrida (repaso conceptual)

No es un entregable con codigo propio: es la base teorica que el
Componente D (Pre-entrega 4) exige aplicar. Estas notas quedan como
referencia rapida de las decisiones de diseno de `fase4_rag_pinecone/`.

## Precision vs Recall

- **Precision@k**: de los `k` documentos recuperados, que proporcion es
  realmente relevante. Precision baja = ruido que confunde al LLM en la
  etapa de generacion.
- **Recall@k**: de todos los documentos relevantes que existen, que
  proporcion aparecio entre los `k` recuperados. Recall bajo = el LLM se
  queda sin el contexto que necesitaba, lo que empuja a alucinar (rellena
  el hueco con conocimiento externo, violando el prompt "filtro de
  veracidad" de la Fase 3).
- **F1-Score**: media armonica entre ambas, para resumir el rendimiento del
  retriever en un solo numero cuando hace falta comparar configuraciones.

## Por que combinar BM25 + embeddings (busqueda hibrida)

- **BM25** (lexico, coincidencia exacta de terminos): fuerte en nombres
  propios, codigos de error, identificadores tecnicos exactos — cosas que
  un embedding puede "difuminar" semanticamente.
- **Embeddings** (semantico): fuerte en sinonimos y significado conceptual,
  pero puede fallar con terminos exactos poco frecuentes en el corpus de
  entrenamiento del modelo.
- La **busqueda hibrida** combina ambos rankings para cubrir los puntos
  ciegos de cada uno por separado.

## RRF (Reciprocal Rank Fusion)

Fusiona rankings de distintas fuentes usando la **posicion** de cada
documento en cada ranking, no sus puntuaciones absolutas — evita el error
de sumar un score BM25 (ej. 20) con una similitud coseno (ej. 0.8), que
viven en escalas completamente distintas y no son comparables
directamente. `EnsembleRetriever` de LangChain (usado en
`fase4_rag_pinecone/rag_system.py`) resuelve esta fusion internamente, en
espiritu equivalente a RRF, sin necesidad de implementarlo a mano.

## Re-ranking con cross-encoders

Etapa opcional posterior al retrieval inicial: reordena con mayor precision
solo el subconjunto top-k ya recuperado. Mucho mas preciso que un
embedding de bi-encoder porque compara query y documento juntos (no por
separado), pero tambien mucho mas lento — por eso se aplica solo a pocos
candidatos, nunca a la busqueda completa sobre todo el indice. No se
implementa en este proyecto (fuera del alcance de la Pre-entrega 4), pero
queda documentado como el siguiente paso logico de esta arquitectura.

## Aplicacion concreta en este proyecto

`fase4_rag_pinecone/rag_system.py` (Componente D) implementa la mitad
practica de este repaso: `RAGSystem` combina un retriever vectorial
(Pinecone) con un `BM25Retriever` local via `EnsembleRetriever`, y
`evaluate.py` mide `Precision@5` / `Recall@5` sobre un golden set de
preguntas con documento fuente conocido — la forma concreta de verificar,
con numeros reales, si la busqueda hibrida efectivamente mejora sobre
buscar solo con embeddings.
