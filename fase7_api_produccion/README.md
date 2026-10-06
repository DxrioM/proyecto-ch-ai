# Pre-entrega 7 — API de producción y monitoreo activo

Expone el orquestador multi-agente de la Fase 6 como una API REST
asíncrona (FastAPI), con persistencia de estado en Redis, observabilidad
activa (LangSmith) y un flujo de aprobación humana (Human-in-the-loop)
antes de ejecutar la acción que este sistema considera "crítica".

## Estado de este componente

> **Validado end-to-end con servicios reales**: Redis (Upstash), LangSmith y
> la API corriendo con uvicorn. Interrupt/resume contra el checkpointer de
> Redis verificado (pausa en `analista`, reanudacion tras aprobacion, respuesta
> final correcta). Prueba de carga de 5 peticiones concurrentes: 5/5 `DONE`.

## Resultados reales

Corrida de `load_test.py` (5 peticiones concurrentes, `MAX_JOBS_CONCURRENTES=2`):

| Metrica | Valor |
|---|---|
| Duracion total del lote | 221.2 s |
| Latencia p95 (local) | 221.2 s |
| Latencia promedio (local) | 84.2 s |
| Latencia por job | 221.2 s, 32.1 s, 93.0 s, 9.1 s, 65.7 s |
| Estados finales | 5 x `DONE` |

Lectura de LangSmith (`export_metrics.py`, filtrado a la ventana de la corrida):

- 6 trazas: 5 `ejecutar_job` + 1 `LangGraph` (el tramo de reanudacion del job
  que pasó por HITL; `reanudar_job` no tiene el decorador `@traced_job`).
- Costo total: US$ 0.007708 (LangSmith calculo el precio del modelo).
- Costo por traza: US$ 0.00068 a 0.00338.
- Tokens por traza: 3 237 a 20 655.
- Latencia p95 segun LangSmith: 219.2 s.

Dashboard: `dashboard.html` (autocontenido, se regenera con
`build_dashboard.py`). Es la vista interactiva que reemplaza las screenshots.

Por que la latencia es alta: el tier gratuito de Groq limita a 8 000 tokens
por minuto. Con 5 peticiones en paralelo, el limite de concurrencia del
worker (semaforo) hace que los jobs esperen en cola, y los reintentos con
backoff suman tiempo. El p95 con 5 muestras es, en la practica, la peticion
mas lenta; conviene leerlo junto con el promedio. Con un plan pago o un
`MAX_JOBS_CONCURRENTES` mas alto, la latencia baja; no lo medimos.

Un intento previo sin semaforo tuvo 3 de 5 jobs en `FAILED` por error 429 de
Groq. El diseño lo manejo bien: el error quedo registrado y el cliente no
quedo en polling infinito.

Checkpointer: se uso una implementacion propia de `BaseCheckpointSaver` sobre
Redis (`app/redis_checkpointer.py`) en lugar de `langgraph-checkpoint-redis`,
porque ese paquete necesita los comandos `FT.*` (RediSearch), que Upstash no
soporta. Solo usa GET, SET, RPUSH, LRANGE y SCAN, con TTL de 7 dias.

## Por qué esta pila de herramientas

- **Redis en la nube (Upstash) en vez de local**: este entorno de
  desarrollo no tiene Docker ni WSL con una distro instalada, y no hay un
  build de Redis nativo confiable para Windows sin instalar un servicio
  adicional. Upstash da un `REDIS_URL` real en minutos, sin tarjeta, y el
  codigo (`redis.asyncio` + `langgraph-checkpoint-redis`) es identico
  apunte a Upstash o a un Redis local - es solo una URL de conexion.
- **LangSmith en vez de Arize Phoenix**: la consigna ofrece ambos como
  equivalentes; se eligio LangSmith.
- **Dashboard HTML dinamico en vez de screenshots estaticas**: este
  entorno no tiene navegador ni herramienta de captura de pantalla
  disponible. En vez de screenshots, `export_metrics.py` trae datos reales
  de la API de LangSmith (latencia, tokens, costo si esta disponible) y
  `dashboard.html` los visualiza de forma interactiva - complementa (no
  reemplaza en espiritu) la evidencia de observabilidad que pide la
  consigna, solo en un formato navegable en vez de una imagen fija.

## Arquitectura

- `app/job_store.py`: `JobStore` — estado de cada job persistido en Redis
  como JSON (`job:{job_id}`), con TTL de 24hs. `GET /tasks/{id}` solo lee
  este estado, nunca espera al agente.
- `app/graph.py`: reutiliza `fase6_orquestador_multiagente.graph.build_graph()`
  tal cual, agregando el checkpointer de Redis (`app/redis_checkpointer.py`) y un
  gate HITL (`_hitl_gate`, inyectado via el parametro `hitl_gate` agregado
  a la Fase 6 especificamente para esto) que pausa el grafo
  (`langgraph.types.interrupt`) justo antes de que el nodo `analista`
  ejecute.
- `app/hitl.py`: define que se considera una accion "critica" en este
  sistema — ver mas abajo.
- `app/worker.py`: corre el grafo en segundo plano (`ejecutar_job`) o lo
  reanuda tras una aprobacion (`reanudar_job`); nunca deja escapar una
  excepcion, siempre actualiza Redis a un estado terminal (`DONE`,
  `FAILED` o `REJECTED`).
- `app/observability.py`: activa el tracing de LangSmith via variables de
  entorno (LangChain/LangGraph trazan sus propias llamadas a LLM
  automaticamente, no hace falta envolver cada una a mano) + un decorador
  `@traced_job` que agrupa toda la ejecucion de un job en una sola traza
  nombrada.
- `app/main.py`: la API. `POST /tasks` encola y devuelve `job_id` de
  inmediato (202, nunca bloquea); `GET /tasks/{id}` lee el estado; `POST
  /tasks/{id}/approve` aprueba o rechaza una tarea pausada en HITL.

## Que se considera una accion "critica" (HITL)

En este sistema, **cualquier pregunta que requiera que el especialista de
Analisis ejecute un calculo** pasa por una pausa de aprobacion humana antes
de que el Analista corra. Las preguntas que solo necesitan investigacion
(busqueda de solo lectura) nunca pasan por el gate. Esto representa, en el
dominio ficticio del proyecto, operaciones con impacto real (ej. calcular
una penalidad de SLA o un reembolso) que una organizacion real querria que
un humano confirme antes de ejecutar — a diferencia de una simple consulta
de informacion, que no necesita supervision.

## Como levantar el entorno

1. Completar en el `.env` de la raiz del proyecto: `GROQ_API_KEY`
   (heredada), `REDIS_URL` (Upstash u otro Redis, formato
   `redis://...`/`rediss://...`), `LANGSMITH_API_KEY`.
2. Instalar dependencias: `pip install -r requirements.txt`.
3. Levantar la API:

   ```bash
   uvicorn fase7_api_produccion.app.main:app --reload
   ```

   Al arrancar, conecta a Redis, crea los indices necesarios (primera vez)
   y arma el grafo. Docs interactivas en `http://127.0.0.1:8000/docs`.

## Como probar manualmente

```bash
# 1. Pregunta que NO requiere aprobacion (solo investigacion)
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"pregunta": "Que base de datos usa el sistema de pedidos?"}'
# -> {"job_id": "...", "status": "PENDING"}

curl http://127.0.0.1:8000/tasks/<job_id>
# -> status pasa de PENDING a RUNNING a DONE

# 2. Pregunta que SI requiere un calculo (dispara el gate HITL)
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"pregunta": "Investiga los tiempos de respuesta por severidad y calculame el promedio en horas."}'

curl http://127.0.0.1:8000/tasks/<job_id>
# -> status = AWAITING_APPROVAL, con interrupt_payload explicando la accion propuesta

curl -X POST http://127.0.0.1:8000/tasks/<job_id>/approve \
  -H "Content-Type: application/json" -d '{"aprobado": true}'
# -> el analista corre, status pasa a DONE
```

## Como lanzar las 5 peticiones concurrentes (prueba de carga)

Con la API corriendo en otra terminal:

```bash
python fase7_api_produccion/load_test.py
```

Lanza 5 preguntas en simultaneo (una de ellas dispara el gate HITL, y el
script la aprueba automaticamente para no bloquear la corrida), mide la
latencia real de cada una, y guarda el resumen (incluida la latencia p95)
en `metrics/load_test_resultado.json`.

Despues, para traer el costo por ejecucion y la latencia p95 segun
LangSmith (no solo medida localmente):

```bash
python fase7_api_produccion/export_metrics.py
```

Esto genera `metrics/dashboard_data.json`, la fuente de datos del dashboard
HTML dinamico (ver mas abajo).

## Dashboard (en vez de screenshots)

`dashboard.html` visualiza `metrics/dashboard_data.json` de forma
interactiva: latencia p95, costo por ejecucion (o conteo de tokens si
LangSmith no tiene precios configurados para el modelo), y el detalle de
las 5 ejecuciones de la prueba de carga. Se genera/actualiza despues de
correr `load_test.py` + `export_metrics.py`.

## Tests sintéticos

`tests/test_fase7_api.py` (en la raíz del repo): `JobStore` con un cliente
Redis falso, `hitl.construir_payload_aprobacion()`, y el flujo completo del
worker (`ejecutar_job`/`reanudar_job`) con `MemorySaver` (misma semántica
de `interrupt()`/resume que `AsyncRedisSaver` — verificado manualmente) y
Supervisor/especialistas falsos: cubre el camino sin HITL, el camino que
pausa en `AWAITING_APPROVAL`, la aprobación, el rechazo, y que una
excepción del agente deja el job en `FAILED` sin crashear.

```bash
python -m pytest tests/test_fase7_api.py -v
```

## Errores comunes evitados

- **Bloquear el Event Loop**: todas las llamadas a Redis
  (`redis.asyncio`), al checkpointer y al LLM son async nativas; los
  endpoints nunca hacen una llamada sincrona bloqueante.
- **Background tasks que fallan en silencio**: `ejecutar_job`/`reanudar_job`
  atrapan cualquier excepción y actualizan Redis a `FAILED` — sin esto, un
  fallo en segundo plano dejaría al cliente esperando en un loop de
  polling infinito (`GET /tasks/{id}` nunca cambiaría de `RUNNING`).
