# Contexto de Proyecto — Fase 1: La interfaz base (conexion y abstraccion de LLMs)

> Este documento es el contexto completo para trabajar la Fase 1 de un proyecto de 8 fases (curso "AI Engineering"). Pensado para pegarlo como contexto inicial en Claude Code y trabajar la implementacion desde ahi.

## 0. Panorama general del proyecto (8 fases)

El proyecto completo tiene 8 modulos/fases, cada uno se aprueba antes de pasar al siguiente:

1. **La interfaz base: conexion y abstraccion de LLMs** ← *Fase actual, unico alcance de este documento*
2. Encadenamiento logico: orquestacion con LangChain
3. Persistencia de datos y vector DBs
4. Escalabilidad documental: RAG avanzado y Pinecone
5. Razonamiento autonomo: agentes con LangGraph
6. Sistemas multi-agente: colaboracion y especializacion
7. Produccion y robustez: observabilidad, costos y despliegue
8. Capstone: entrega final

**No implementar nada de las fases 2-8 todavia.** Este documento solo cubre la Fase 1.

## 1. Objetivo de la Fase 1

Construir la capa de abstraccion base para interactuar con LLMs usando Python 3.12+, `asyncio` y SDKs oficiales, de forma que:

- El codigo sea agnostico al proveedor (OpenAI, Anthropic, Gemini, etc.).
- Todas las llamadas a modelos sean no bloqueantes (`async`/`await`).
- El sistema sea resiliente ante latencia, timeouts y rate limits.

La Fase 1 tiene **dos entregables independientes** que deben implementarse ambos.

---

## 2. Entregable A — Ejercicio: "Orquestador Concurrente de Modelos"

Simulacion de la logica de un backend que consulta multiples fuentes de IA de forma eficiente (sin llamar APIs reales; solo simula latencia con `asyncio.sleep`).

### Pasos requeridos

1. Entorno Python 3.12+.
2. Definir tres corrutinas `async def` que simulen llamadas a distintos modelos: `gpt_4_call`, `claude_3_call`, `local_llama_call`. Cada una usa `await asyncio.sleep(t)` con un tiempo distinto para simular latencia de red (no usar `time.sleep`).
3. Una funcion orquestadora dispara las tres llamadas simultaneamente con `asyncio.gather`.
4. Envolver la ejecucion total en `asyncio.timeout(2.0)`. Si alguna llamada tarda mas, capturar `TimeoutError` y mostrar un mensaje de error sin detener el programa.
5. Usar `asyncio.Semaphore` para que, aunque se disparen 10 simulaciones de llamadas, solo 2 corran al mismo tiempo.

### Criterios de aceptacion

- El codigo no debe usar `time.sleep` (bloqueante).
- Los logs deben mostrar que las tareas inician casi al mismo tiempo (timestamps de inicio muy cercanos entre si).
- Manejo correcto de la excepcion `TimeoutError` (no debe crashear el programa).

### Rubrica de evaluacion (100 pts, aprobacion 60 pts)

| Criterio | Descripcion | Peso |
|---|---|---|
| Implementacion de asincronia y no bloqueo | Uso correcto de `async`/`await`, evitar `time.sleep` | 30% |
| Gestion de concurrencia con `asyncio.gather` | Orquestar llamadas simultaneas y procesar resultados colectivamente | 25% |
| Control de flujo con semaforos | Uso de `asyncio.Semaphore` para limitar recursos concurrentes | 25% |
| Resiliencia y manejo de timeouts | Limites de tiempo + captura de excepciones sin romper el programa | 20% |

### Entregable

- Tipo: **archivo (PDF)**. El PDF debe contener el codigo y evidencia de ejecucion (logs/salida por consola mostrando timestamps, timeouts capturados y el efecto del semaforo).

---

## 3. Entregable B — Pre-entrega 1: "Cliente de LLM robusto y asincrono"

A diferencia del Entregable A (simulado), aqui se construye un cliente **real** que habla con proveedores de IA de verdad, con una interfaz unificada ("Unified Async LLM Client").

### Que construir

Un repositorio de codigo (o modulo Python estructurado) en Python 3.12+ que permita:

1. **Intercambiabilidad**: instanciar un proveedor (OpenAI, Anthropic, Gemini, etc.) bajo una interfaz comun, sin cambiar la logica de negocio.
2. **Asincronia**: todas las llamadas a modelos son no bloqueantes (`async`/`await`), usando los SDKs oficiales en su version async (`AsyncOpenAI`, `AsyncAnthropic`, `genai.Client(...).aio`, etc.).
3. **Streaming**: un metodo que devuelva un generador asincrono de tokens (`async for` + `yield`).
4. **Validacion**: Pydantic para la estructura de mensajes de entrada y configuracion del modelo.

### Pasos sugeridos

1. `schemas.py`: definir con Pydantic `ChatMessage` (role, content), `LLMConfig` (proveedor, modelo, api keys, temperature, max_tokens) y `ModelResponse` (proveedor, modelo, content, error opcional).
2. `BaseLLMClient`: clase base abstracta (ABC) con `async def generate(...)` y `async def generate_stream(...)` (generador asincrono).
3. Un cliente concreto por proveedor (ej. `OpenAIClient`, `AnthropicClient`, `GeminiClient` o los que se elijan segun las keys gratuitas disponibles — ver seccion 5), heredando de `BaseLLMClient`.
4. `AsyncLLMManager` (patron Factory): recibe un `LLMConfig` e instancia internamente el cliente correcto segun el proveedor. Expone `generate()` y `generate_stream()` de forma agnostica al proveedor.
5. `main.py`: script de validacion que carga `.env`, crea el manager y hace una pregunta corta ("Que es la entropia?") tanto en modo normal como en streaming.

### Errores comunes a evitar

- **Bloqueo del Event Loop**: nunca usar la version sincrona de un SDK dentro de una funcion `async`. Siempre `await cliente.metodo_async(...)`.
- **Fuga de excepciones**: un error de API key invalida, rate limit o conexion no debe romper el loop principal. Capturar la excepcion especifica del SDK (`RateLimitError`, `APIConnectionError`, `APIError`, etc.) y devolver un `ModelResponse` con el campo `error` seteado (o un chunk de error en el streaming), nunca dejar que la excepcion escape sin control.

### Entregable

- Tipo: **repositorio**. Debe incluir: clientes async implementados, `schemas.py`, `.env.example` (variables necesarias, sin valores reales), script de prueba de streaming, y `README.md` explicando como ejecutar y que variables de entorno se necesitan.

### Referencia de arquitectura (ejemplo resuelto, usar como guia de diseno)

Existe un notebook de referencia (`Pista_Pre_entrega_1_Cliente_de_LLM_robusto_y_asincrono.ipynb`) con una solucion completa que sigue exactamente este patron:

- `Provider(str, Enum)` con los proveedores soportados.
- `ChatMessage`, `LLMConfig`, `ModelResponse` en Pydantic (con `SecretStr` para las API keys).
- `BaseLLMClient(ABC)` con `generate()` y `generate_stream()` abstractos.
- Un cliente por proveedor implementando ambos metodos, capturando las excepciones propias del SDK y devolviendo siempre un `ModelResponse` (nunca dejando escapar la excepcion).
- `AsyncLLMManager` como Factory: en `__init__` recibe `LLMConfig` y arma el cliente concreto; expone `generate()`/`generate_stream()` delegando al cliente interno.
- Diferencias clave por SDK a tener en cuenta al implementar cada cliente:
  - OpenAI: `response.choices[0].message.content`; streaming con `stream=True` + `async for chunk in stream`.
  - Anthropic: `response.content[0].text`; `max_tokens` es obligatorio; streaming con `async with client.messages.stream(...) as stream: async for texto in stream.text_stream`.
  - Gemini: separa el `system` prompt del resto de mensajes (`system_instruction` aparte); el rol del asistente se llama `"model"`, no `"assistant"`; streaming con `generate_content_stream(...)` + `async for`.

No es obligatorio copiar este notebook tal cual — es una referencia de diseno para no reinventar la arquitectura, pero se recomienda adaptarlo al set de proveedores que efectivamente se vaya a usar (ver seccion 5).

---

## 4. Requisitos transversales (pedidos explicitamente por el usuario)

Aplican a **ambos** entregables:

1. **Python 3.12+**, trabajo asincrono real entre modelos (nada de `time.sleep`).
2. **Codigo principalmente en ingles**: nombres de variables, funciones, clases, comentarios de codigo, docstrings → en ingles.
3. **Texto de cara al usuario en espanol, sin caracteres especiales**: todo mensaje impreso en consola, logs visibles, mensajes de error mostrados al usuario, docstrings de negocio orientados a lectura humana en espanol → deben ir sin tildes ni "ñ" (ej. "El modelo tardo demasiado" en vez de "El modelo tardó demasiado", "configuracion" en vez de "configuración").
4. Generar **`.env`** (con las variables reales del usuario, NO versionarlo) y su correspondiente **`.env.example`** (mismas claves, sin valores).
5. Generar **`.gitignore`** cubriendo al menos: `.env`, `__pycache__/`, `*.pyc`, entornos virtuales (`.venv/`, `venv/`), `.pytest_cache/`, artefactos de IDE.
6. **Preferir proveedores de IA gratuitos** en la mayoria de los casos (ver seccion 5) para poder correr y validar el codigo sin costo.

---

## 5. Recomendacion de proveedores de IA gratuitos (verificado agosto 2026)

Para el Entregable B se necesitan llamadas reales. Recomendacion pensada para minimizar costo y friccion (sin tarjeta de credito donde sea posible):

| Proveedor | Costo | Tarjeta requerida | Notas |
|---|---|---|---|
| **Google Gemini** | Free tier disponible | No | `aistudio.google.com/apikey`. Limites variables por modelo (ej. Gemini 2.5 Flash-Lite: ~15 RPM / 1000 req/dia; Gemini 2.5 Flash: ~10 RPM / 250 req/dia). Google ajusta estos limites sin previo aviso, conviene revisar la consola antes de correr pruebas masivas. |
| **Groq** | Free tier disponible | No | `console.groq.com`. Muy rapido (hardware LPU). Ideal para simular `local_llama_call` de forma real: sirve modelos Llama (ej. `llama-3.1-8b-instant`, `llama-3.3-70b`) gratis, ~30 RPM / hasta 14,400 req/dia segun modelo. |
| **Ollama (local)** | 100% gratis | No aplica (corre en tu maquina) | Sin API key. Alternativa genuina para `local_llama_call`: corre un modelo Llama localmente. Requiere instalar Ollama y descargar un modelo (ej. `llama3.1`), pero no depende de ningun servicio externo ni limite de cuota. |
| OpenAI | Pago desde el primer uso | Si | Solo si el usuario ya tiene creditos/billing configurado. No es gratis. |
| Anthropic | Pago desde el primer uso | Si | Igual que OpenAI, no tiene free tier utilizable sin tarjeta. |

**Sugerencia concreta para el Entregable B**: usar **Gemini** y **Groq** como los dos (o tres, sumando Ollama) proveedores reales detras de la interfaz unificada — ambos gratuitos y sin tarjeta. Si se quiere mantener la nomenclatura del Entregable A (`gpt_4_call`, `claude_3_call`, `local_llama_call`) como inspiracion de nombres de proveedores/modelos en el Entregable B, se puede mapear:
- `claude_3_call` → proveedor Gemini (o Anthropic si el usuario decide pagar).
- `gpt_4_call` → proveedor Groq (modelo grande, ej. `llama-3.3-70b-versatile`).
- `local_llama_call` → Ollama local o Groq con `llama-3.1-8b-instant`.

El Entregable A no llama APIs reales (todo es `asyncio.sleep` simulando latencia), asi que no necesita ninguna key.

---

## 6. Estructura de proyecto sugerida

```
proyecto_ch_ai/
├── .env                  # valores reales (NO se commitea)
├── .env.example          # mismas claves, sin valores
├── .gitignore
├── README.md
├── requirements.txt       # o pyproject.toml
├── entregable_a_orquestador/
│   └── orquestador_concurrente.py   # Ejercicio: simulacion con gather + semaphore + timeout
└── entregable_b_llm_client/
    ├── schemas.py          # ChatMessage, LLMConfig, ModelResponse (Pydantic)
    ├── base_client.py      # BaseLLMClient (ABC)
    ├── gemini_client.py
    ├── groq_client.py
    ├── llm_manager.py      # AsyncLLMManager (Factory)
    └── main.py             # script de validacion (modo normal + streaming)
```

---

## 7. Checklist final antes de dar la Fase 1 por aprobada

- [ ] Entregable A: 3 corrutinas simuladas + `gather` + `Semaphore(2)` sobre 10 llamadas + `timeout(2.0)` + manejo de `TimeoutError`, todo sin `time.sleep`.
- [ ] Entregable A: logs muestran inicio casi simultaneo de las tareas.
- [ ] Entregable A: exportado/documentado en PDF.
- [ ] Entregable B: `BaseLLMClient` (ABC) + al menos 2 clientes reales funcionando (gratis, sin tarjeta) + `AsyncLLMManager` (Factory).
- [ ] Entregable B: streaming funcionando con generador asincrono.
- [ ] Entregable B: validacion con Pydantic (`LLMConfig`, `ChatMessage`, `ModelResponse`).
- [ ] Entregable B: ninguna excepcion de proveedor se escapa sin control (siempre vuelve como `ModelResponse.error` o chunk de error).
- [ ] `.env` + `.env.example` + `.gitignore` presentes.
- [ ] `README.md` explica como correr el proyecto y que variables de entorno se necesitan.
- [ ] Codigo (nombres, comentarios) en ingles; mensajes al usuario en espanol sin tildes/ñ.
