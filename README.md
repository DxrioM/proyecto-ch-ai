# Proyecto AI Engineering

Proyecto de 8 fases del curso "AI Engineering". Cada fase se documenta en su
propio `contexto_faseN.md` y se implementa en su propia carpeta. Este README
cubre la Fase 1 y la Fase 2; a medida que se aprueben las siguientes fases se
van agregando sus secciones.

- Fase 1: [contexto_fase1.md](contexto_fase1.md) — interfaz base, conexion y
  abstraccion de LLMs.
- Fase 2: [contexto_fase2.md](contexto_fase2.md) — encadenamiento logico,
  orquestacion con LangChain.

## Estructura

```
proyecto_ch_ai/
├── .env                          # claves reales (NO se versiona)
├── .env.example                  # mismas claves, sin valores
├── .gitignore
├── conftest.py                   # hace importable la raiz del repo para pytest
├── requirements.txt
├── tests/
│   └── test_fase2_resilience.py  # tests sinteticos de with_retry() / ValidationError
├── entregable_a_orquestador/            # Fase 1 - Entregable A
│   ├── orquestador_concurrente.py
│   ├── evidencia_ejecucion.log   # salida de consola capturada
│   └── entregable_a_evidencia.pdf
├── entregable_b_llm_client/             # Fase 1 - Entregable B
│   ├── schemas.py                # ChatMessage, LLMConfig, ModelResponse (Pydantic)
│   ├── base_client.py            # BaseLLMClient (ABC)
│   ├── gemini_client.py
│   ├── groq_client.py
│   ├── openai_client.py
│   ├── llm_manager.py            # AsyncLLMManager (Factory)
│   └── main.py                   # script de validacion (modo normal + streaming)
├── fase2_lcel_refactor/                 # Fase 2 - Componente A
│   └── main.py                   # prompt | model | StrOutputParser, con ainvoke
├── fase2_ejercicio_validacion/          # Fase 2 - Componente B
│   └── entity_extraction.py      # with_structured_output + with_retry
└── fase2_pipeline_validado/             # Fase 2 - Componente C (Pre-entrega 2)
    ├── schemas.py                # TechExtraction (Pydantic)
    ├── chain.py                  # cadena LCEL + process_text()
    ├── main.py                   # mini-script de prueba
    └── README.md                 # detalle del pipeline + ejemplo de salida
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

---

# Fase 2 — Encadenamiento logico: orquestacion con LangChain

Reemplaza el `AsyncLLMManager` propio de la Fase 1 por cadenas declarativas
de LangChain (LCEL). Ver [contexto_fase2.md](contexto_fase2.md) para el
detalle completo de la consigna. Proveedor usado en los tres componentes:
**Groq** (`ChatGroq`, gratis, sin tarjeta), modelo `openai/gpt-oss-120b`.

## Componente A — Refactorizacion a LCEL Asincrono

`fase2_lcel_refactor/main.py`: reemplaza la llamada manual al SDK del
Modulo 1 por una cadena `prompt | model | StrOutputParser()`, con
`ChatPromptTemplate` (roles System/Human) y ejecucion asincrona
(`await chain.ainvoke({"pregunta": "..."})`). El resultado es texto plano,
no un `AIMessage`.

```bash
python fase2_lcel_refactor/main.py
```

## Componente B — Validacion estructurada y resiliencia

`fase2_ejercicio_validacion/entity_extraction.py`: resuelve el ejercicio de
la catedra (`with_structured_output` + `with_retry`), adaptado de
`ChatOpenAI` a `ChatGroq`. Define `EntityExtraction` (Pydantic: `topic`,
`entities`, `sentiment_score` entre 0 y 1, `complexity_level` opcional),
arma `structured_llm = llm.with_structured_output(EntityExtraction)` y
`resilient_llm = structured_llm.with_retry(stop_after_attempt=3,
wait_exponential_jitter=True)`, y ejecuta la cadena dentro de un
`try/except` que nunca deja escapar la excepcion.

```bash
python fase2_ejercicio_validacion/entity_extraction.py
```

## Componente C — Pipeline de Extraccion de Entidades Tecnicas (Pre-entrega 2)

El entregable principal de la Fase 2. Ver el detalle, el ejemplo de salida
JSON y el resultado de la prueba de estres en
[fase2_pipeline_validado/README.md](fase2_pipeline_validado/README.md).

```bash
python -m fase2_pipeline_validado.main
```

## Variables de entorno (Fase 2)

Reutiliza las mismas variables de la Fase 1 (`.env` en la raiz). Los tres
componentes de la Fase 2 solo necesitan `GROQ_API_KEY`.

## Tests sinteticos de resiliencia

`tests/test_fase2_resilience.py` prueba `with_retry()` y el manejo de
`ValidationError` de los Componentes B y C con un modelo falso (no llama a
la API real ni gasta cuota). Ver el detalle en
[fase2_pipeline_validado/README.md](fase2_pipeline_validado/README.md#tests-sinteticos-sin-llamar-a-la-api-real).

```bash
python -m pytest tests/ -v
```

## Errores comunes evitados (especificos de LangChain)

- **Olvidar el `await`**: `chain.ainvoke(...)` devuelve una corrutina; sin
  `await` no se ejecuta la llamada.
- **Prompts hardcodeados**: nada de f-strings sueltas dentro de una cadena;
  siempre `ChatPromptTemplate`, para que LangChain gestione las variables de
  entrada y estas coincidan con las claves pasadas a `ainvoke`.
- **JSON invalido o incompleto del LLM**: `with_structured_output()` valida
  contra el esquema Pydantic; `with_retry()` reintenta ante ese fallo o ante
  errores transitorios de red/rate limit, en vez de romper el programa.
