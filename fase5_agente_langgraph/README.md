# Pre-entrega 5 — Agente de razonamiento ciclico con memoria persistente

Agente ReAct construido con LangGraph: decide por si mismo cuando llamar a
una herramienta en base al prompt del usuario (sin rutas `if`/`else`
manuales), puede encadenar mas de una llamada a herramientas para llegar a
una conclusion, y recuerda interacciones previas dentro de una misma sesion
(`thread_id`) gracias a un checkpointer SQLite.

Continua el dominio ficticio del "Sistema de Pedidos Online" usado en las
Fases 3 y 4 — antes se consultaba via RAG (texto no estructurado), ahora un
agente lo consulta via herramientas (datos estructurados).

## Arquitectura

- `tools.py`: `buscar_pedidos(cliente_id)` y `obtener_detalle_pedido(pedido_id)`,
  decoradas con `@tool`. El LLM elige cual usar (y cuando encadenar ambas)
  **unicamente** en base al docstring de cada una — por eso son
  deliberadamente descriptivas. Ambas devuelven `{"error": "..."}` en vez
  de lanzar una excepcion si el cliente/pedido no existe, para que el
  agente pueda razonar sobre el error en vez de que el programa se rompa.
- `graph.py`: `StateGraph(MessagesState)` con un nodo `agent` (el LLM, con
  `bind_tools()`) y un nodo `tools` (`ToolNode`), conectados por una arista
  condicional (`tools_condition`): si el ultimo mensaje del LLM tiene
  `tool_calls`, rutea a `tools`; si no, termina. Esa arista — no un
  `if`/`else` escrito a mano — es la que decide el flujo.
- `main.py`: corre 3 turnos sobre el mismo `thread_id`, con
  `recursion_limit=10` para evitar bucles infinitos, y guarda la traza
  completa en `traces/ejemplo_traza.json`.

## Como levantar el entorno

Requiere `GROQ_API_KEY` en el `.env` de la raiz del proyecto (igual que las
fases anteriores).

```bash
pip install -r requirements.txt
python -m fase5_agente_langgraph.main
```

Esto corre la demo completa y regenera `checkpoints.sqlite` (el archivo de
persistencia, no se versiona — se recrea solo) y `traces/ejemplo_traza.json`.

## Ejemplo de traza (razonamiento ciclico real, no simulado)

Las 3 interacciones de `main.py`, corridas sobre el **mismo** `thread_id`
(`traces/ejemplo_traza.json` tiene la traza completa, 12 mensajes):

**Turno 1 — pregunta inicial (1 herramienta):**

```
Usuario: Cuantos pedidos tuvo el cliente 102 y cual fue el total?
→ El agente decide llamar: buscar_pedidos(cliente_id=102)
→ La herramienta devuelve: {"pedidos": 3, "total": 14500.0, "pedido_ids": [5001, 5002, 5003]}
→ Respuesta: "El cliente 102 tiene 3 pedidos en total, y el monto
  acumulado de sus compras es $14.500,00."
```

**Turno 2 — mismo thread_id, memoria + 2da herramienta (razonamiento multi-paso):**

```
Usuario: Y cual es el detalle del ultimo pedido?
→ El agente RECUERDA que se hablaba del cliente 102 (no se lo repiti),
  deduce que "el ultimo pedido" es el ID 5003 (del turno anterior), y
  decide llamar: obtener_detalle_pedido(pedido_id=5003)
→ La herramienta devuelve: {"id": 5003, "fecha": "2026-09-15", "monto": 4000.0,
  "estado": "en camino", "productos": ["Silla ergonomica"]}
→ Respuesta: detalle completo del pedido 5003.
```

**Turno 3 — ciclo de retorno ante un error (cliente inexistente):**

```
Usuario: Cuantos pedidos tuvo el cliente 999?
→ El agente decide llamar: buscar_pedidos(cliente_id=999)
→ La herramienta devuelve: {"error": "No se encontro ningun cliente con ID 999"}
→ El agente NO alucina un resultado: explica el error y pide confirmar el dato.
Respuesta: "No se encontró ningún cliente con el ID 999 en nuestro sistema.
Por favor, verifica el número e inténtalo de nuevo."
```

## Tests sinteticos

`tests/test_fase5_agent.py` (en la raiz del repo) prueba:

- Las herramientas de forma determinista (sin LLM): caso de exito y caso
  de error para cada una.
- El ruteo del grafo (`tools_condition`) con un LLM falso: que el grafo
  ejecute la herramienta **real** cuando el modelo decide llamarla, que
  termine sin llamar a nada cuando no hace falta, y que la memoria entre
  turnos (mismo `thread_id`) efectivamente acumule el historial — todo sin
  gastar cuota de la API real ni depender de que el LLM "decida" lo mismo
  en cada corrida de tests.

```bash
python -m pytest tests/test_fase5_agent.py -v
```

## Decisiones de diseño

- **`AsyncSqliteSaver`** (de `langgraph-checkpoint-sqlite`) en vez de la
  variante sincronica `SqliteSaver`: todo el proyecto es async desde la
  Fase 1, y el grafo invoca el LLM con `ainvoke()`.
- **Limite de recursion = 10**: techo explicito para que un eventual bucle
  del agente (ej. el LLM reintentando una herramienta sin converger) no
  genere llamadas infinitas a la API.
- **Las herramientas nunca lanzan excepciones**: devuelven `{"error": ...}`,
  mismo criterio de resiliencia que `ModelResponse.error` (Fase 1) y
  `RagResponse.encontrado_en_contexto=False` (Fase 3/4) — el LLM recibe el
  error como dato y decide como responder, en vez de que el programa se
  rompa.
