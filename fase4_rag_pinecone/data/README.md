# Dataset

Este componente **reutiliza el corpus de** [`fase3_rag_local/data/`](../../fase3_rag_local/data/)
(la documentacion ficticia del "Sistema de Pedidos Online": arquitectura,
despliegue, troubleshooting, politicas de soporte) en vez de duplicarlo
aca.

Es deliberado: la consigna de la Fase 4 dice literalmente que se escala
"esa misma logica" de la Fase 3 a la nube — mismo corpus, mismo chunking,
mismo LLM de generacion, pero ahora indexado en Pinecone en vez de
ChromaDB local, con recuperacion hibrida (vectorial + BM25) y evaluacion
cuantitativa (`Precision@5` / `Recall@5`) encima. Ver
[`fase4_rag_pinecone/ingest.py`](../ingest.py).
