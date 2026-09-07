# Componente A — Embeddings y Similitud: la Geometria del Lenguaje

Entregable en PDF (`componente_a_evidencia.pdf`), generado a partir de una
corrida real (no valores de ejemplo).

- `embeddings_similitud.py`: define 5 oraciones sobre el mismo concepto
  tecnico ("despliegue independiente de microservicios") con vocabulario
  distinto entre si, mas 2 oraciones trampa que comparten palabras clave
  literales pero significan algo no relacionado. Calcula embeddings reales
  (el mismo modelo local que usan los Componentes C y D:
  `DefaultEmbeddingFunction` de Chroma) y la matriz de Similitud Coseno
  entre las 7 con `scikit-learn`.

Ejecutar:

```bash
python fase3_embeddings_similitud/embeddings_similitud.py
```

El PDF (`componente_a_evidencia.pdf`) incluye: las 7 oraciones, el
fragmento de codigo de similitud coseno, la matriz de resultados real, un
analisis honesto (el promedio agregado y una comparacion mas fina: cada
trampa contra la oracion de concepto con la que comparte palabra clave
literal, comparada contra el promedio de esa oracion con sus verdaderos
pares semanticos), y el diagrama de flujo de busqueda semantica pedido por
la consigna.
