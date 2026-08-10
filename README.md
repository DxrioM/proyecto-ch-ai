# Fase 1 — La interfaz base: conexion y abstraccion de LLMs

Proyecto de la Fase 1 del curso "AI Engineering". Contiene los dos entregables
independientes descritos en [contexto_fase1.md](contexto_fase1.md).

## Estructura

```
proyecto_ch_ai/
├── .env                          # claves reales (NO se versiona)
├── .env.example                  # mismas claves, sin valores
├── .gitignore
├── requirements.txt
├── entregable_a_orquestador/
│   ├── orquestador_concurrente.py
│   ├── evidencia_ejecucion.log   # salida de consola capturada
│   └── entregable_a_evidencia.pdf
└── entregable_b_llm_client/
    ├── schemas.py                # ChatMessage, LLMConfig, ModelResponse (Pydantic)
    ├── base_client.py            # BaseLLMClient (ABC)
    ├── gemini_client.py
    ├── groq_client.py
    ├── openai_client.py
    ├── llm_manager.py            # AsyncLLMManager (Factory)
    └── main.py                   # script de validacion (modo normal + streaming)
```

## Requisitos

- Python 3.12+
- Un entorno virtual (`.venv`)

## Instalacion

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Entregable A — Orquestador Concurrente de Modelos

Simulacion pura (no llama APIs reales): tres corrutinas (`gpt_4_call`,
`claude_3_call`, `local_llama_call`) simulan latencia con `asyncio.sleep`.

- Demo 1: las tres corren en paralelo con `asyncio.gather`, acotadas por
  `asyncio.timeout(2.0)`. Como `local_llama_call` tarda 3.0s, se dispara
  `TimeoutError`, se captura y el programa sigue vivo.
- Demo 2: 10 llamadas simuladas se lanzan a la vez, pero un
  `asyncio.Semaphore(2)` limita a 2 ejecuciones concurrentes por vez.

Ejecutar:

```bash
python entregable_a_orquestador/orquestador_concurrente.py
```

La evidencia de una corrida ya quedo capturada en
`entregable_a_orquestador/evidencia_ejecucion.log` y compilada junto con el
codigo en `entregable_a_orquestador/entregable_a_evidencia.pdf` (el
entregable en formato PDF pedido por la consigna).

## Entregable B — Cliente de LLM robusto y asincrono

Cliente unificado ("Unified Async LLM Client") con interfaz comun para
distintos proveedores, 100% asincrono (`async`/`await`), con streaming y
validacion con Pydantic.

Proveedores implementados:

- **Gemini** (`google-genai`) — gratis, sin tarjeta.
- **Groq** (`groq`) — gratis, sin tarjeta; sirve modelos Llama.
- **OpenAI** (`openai`) — de pago; se incluye principalmente como prueba de
  resiliencia: si no se configura `OPENAI_API_KEY` (o es invalida), el
  cliente debe devolver el error dentro de `ModelResponse.error` (o como
  chunk de streaming) en vez de romper el programa.

### Variables de entorno

Copiar `.env.example` a `.env` y completar las que se vayan a usar:

| Variable | Proveedor | Obligatoria |
|---|---|---|
| `GOOGLE_API_KEY` | Gemini (`aistudio.google.com/apikey`) | Para probar Gemini |
| `GROQ_API_KEY` | Groq (`console.groq.com`) | Para probar Groq |
| `OPENAI_API_KEY` | OpenAI | Opcional (a proposito, para la prueba de resiliencia) |

### Ejecutar el script de validacion

Desde la raiz del proyecto (usa import relativo dentro del paquete):

```bash
python -m entregable_b_llm_client.main
```

El script:

1. Carga `.env`.
2. Por cada proveedor con key configurada, crea un `AsyncLLMManager` y hace
   la pregunta "Que es la entropia?" en modo normal y en modo streaming.
3. Prueba OpenAI a proposito sin key valida (si no se configuro
   `OPENAI_API_KEY`) para demostrar el manejo de errores sin crash.

### Arquitectura

- `ChatMessage`, `LLMConfig`, `ModelResponse`: modelos Pydantic para validar
  entrada/salida antes de tocar cualquier SDK.
- `BaseLLMClient` (ABC): contrato comun (`generate`, `generate_stream`) que
  cada cliente de proveedor debe cumplir.
- `OpenAIClient` / `GeminiClient` / `GroqClient`: implementan el contrato
  usando el SDK async oficial de cada proveedor, capturando siempre las
  excepciones propias del SDK y devolviendo un `ModelResponse` con `error`
  seteado (nunca dejan escapar la excepcion).
- `AsyncLLMManager` (Factory): recibe un `LLMConfig` y arma internamente el
  cliente correcto; el resto del codigo solo habla con el manager, agnostico
  al proveedor.

### Errores comunes evitados

- **Bloqueo del event loop**: todos los clientes usan exclusivamente los
  SDKs async (`AsyncOpenAI`, `genai.Client(...).aio`, `AsyncGroq`).
- **Fuga de excepciones**: ninguna excepcion de proveedor (rate limit, error
  de conexion, key invalida) rompe el programa; siempre vuelve como
  `ModelResponse.error` o como chunk de error en streaming.
