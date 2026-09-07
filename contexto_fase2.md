# Contexto de Proyecto — Fase 2: Encadenamiento logico (orquestacion con LangChain)

> Continuacion de `contexto_fase1.md`. Este documento cubre unicamente la Fase 2 (Modulo 2 del curso "AI Engineering"): "Encadenamiento logico: orquestacion con LangChain". Pensado para pegarlo como contexto en Claude Code una vez que la Fase 1 ya fue aprobada.

## 0. Relacion con la Fase 1

En la Fase 1 se construyo un `AsyncLLMManager` propio (ABC + Factory) que hablaba directo con los SDKs de cada proveedor (OpenAI/Anthropic/Gemini/Groq). En la Fase 2 se reemplaza esa capa manual por **LangChain** y su lenguaje declarativo **LCEL** (`prompt | model | parser`). No hace falta seguir manteniendo el `AsyncLLMManager` de la Fase 1 dentro de las cadenas LCEL: LangChain ya trae sus propios wrappers de modelo (`ChatOpenAI`, `ChatAnthropic`, `ChatGoogleGenerativeAI`, `ChatGroq`, etc.) que cumplen el mismo rol de abstraccion. Lo que si se reutiliza conceptualmente es la carga de API keys desde `.env`.

La Fase 2 tiene **tres componentes evaluables**: dos ejercicios de unidad + una pre-entrega.

---

## 1. Objetivo de la Fase 2

Diseñar y ejecutar cadenas logicas de procesamiento usando LangChain y LCEL para flujos de trabajo predecibles, incorporando:

- Composicion declarativa de Prompt + Modelo + Parser con el operador `|`.
- Ejecucion asincrona (`ainvoke`, `abatch`, `astream`) en vez de imperativa.
- Salidas estructuradas y validadas con Pydantic (`with_structured_output`).
- Resiliencia ante fallos transitorios y de formato (`with_retry`).

---

## 2. Componente A — Ejercicio: "Refactorizacion a LCEL Asincrono"

Migrar la implementacion imperativa del Modulo 1 (SDKs crudos) a una arquitectura declarativa con LCEL.

### Que debe lograr el script final

- Reemplazar la llamada manual al SDK del Modulo 1 por un modelo de LangChain (`ChatOpenAI`, `ChatAnthropic`, o el wrapper del proveedor gratuito elegido — ver seccion 5).
- Componer `prompt | modelo | parser` con el operador `|`.
- Ejecutar la cadena con `await chain.ainvoke({...})`.
- Tomar una pregunta del usuario como diccionario (ej. `{"pregunta": "..."}`) y devolver la respuesta como **texto plano** (no un objeto `AIMessage`).

### Pasos sugeridos

1. Instalar `langchain`, el paquete del proveedor elegido (`langchain-openai`, `langchain-anthropic`, `langchain-google-genai`, `langchain-groq`) y `python-dotenv`.
2. Instanciar el modelo de LangChain con `temperature` y `model_name`/`model` configurados.
3. Definir el prompt con `ChatPromptTemplate.from_messages([...])`, con roles System/Human y al menos una variable (ej. `pregunta` o `contexto`).
4. Construir la cadena: `prompt | model | StrOutputParser()`.
5. Crear una funcion `async def main()` que ejecute la cadena con `.ainvoke()` pasando un diccionario.

### Criterios de aceptacion

- El flujo principal usa exclusivamente sintaxis LCEL (`|`).
- La ejecucion es asincrona (`await chain.ainvoke(...)`).
- La salida es texto plano extraido con `StrOutputParser` (no el `BaseMessage` completo).
- El prompt usa `ChatPromptTemplate` con roles definidos (System/Human).

### Errores comunes a evitar

- Olvidar el `await` en `ainvoke` (devuelve una corrutina, no el resultado).
- Que las llaves `{variable}` del prompt no coincidan exactamente con las claves del diccionario pasado a `ainvoke`.

### Rubrica (100 pts, aprobacion 65 pts)

| Criterio | Descripcion | Peso |
|---|---|---|
| Implementacion de sintaxis LCEL | Uso correcto del operador `\|` para componer la cadena | 30% |
| Gestion de asincronia | Ejecucion correcta con el paradigma asincrono de Python | 25% |
| Configuracion de componentes y prompting | `ChatPromptTemplate` con roles + configuracion del modelo | 25% |
| Post-procesamiento y estructura del repo | Extraccion con `StrOutputParser` + organizacion profesional del codigo | 20% |

### Entregable

- Tipo: **repositorio**. Repo (o estructura local) con la refactorizacion del cliente del Modulo 1: un archivo Python que define y ejecuta una cadena LCEL asincrona con `ChatPromptTemplate`, un modelo de LangChain y `StrOutputParser`.

---

## 3. Componente B — Ejercicio de codigo: "Validacion estructurada y resiliencia en cadenas"

Ejercicio de unidad (con codigo inicial tipo TODO y solucion de referencia provista por la catedra) centrado en `with_structured_output` + `with_retry`. No tiene un tipo de entregable formal separado en el temario (no exige PDF ni repo aparte), pero **si tiene rubrica de evaluacion propia**, asi que conviene resolverlo igual dentro del repo de la Fase 2 (por ejemplo en una carpeta `ejercicio_validacion/` o como test adicional).

### Enunciado

Completar el siguiente esqueleto (los `TODO`) para que la cadena extraiga entidades de un texto de forma validada y resiliente:

```python
import asyncio
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# TODO 1: Define la clase Pydantic 'EntityExtraction'
# Debe tener: topic (str), entities (Lista de str), y sentiment_score (float entre 0 y 1)
class EntityExtraction(BaseModel):
    pass

async def run_validated_chain(text: str):
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    # TODO 2: Configura el modelo para usar la salida estructurada con Pydantic
    # Tip: Usa el metodo .with_structured_output()
    structured_llm = None

    # TODO 3: Agrega una estrategia de reintento con .with_retry()
    # para que sea resiliente ante fallos de conexion (maximo 3 intentos).
    resilient_llm = None

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Analiza el texto y extrae las entidades."),
        ("human", "{input}")
    ])

    # TODO 4: Une el prompt con el resilient_llm y ejecuta asincronamente
    # No olvides manejar excepciones con try/except para capturar fallos de validacion
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    sample_text = "LangGraph es una extension de LangChain para agentes ciclicos."
    asyncio.run(run_validated_chain(sample_text))
```

### Solucion de referencia (arquitectura esperada, adaptar nombres de proveedor segun la seccion 5)

- `EntityExtraction(BaseModel)`: `topic: str`, `entities: List[str]`, `sentiment_score: float = Field(ge=0, le=1)`, y opcionalmente `complexity_level: Optional[str]` con `pattern="^(Low|Medium|High)$"`.
- `structured_llm = llm.with_structured_output(EntityExtraction)`.
- `resilient_llm = structured_llm.with_retry(stop_after_attempt=3, wait_exponential_jitter=True)`.
- `chain = prompt | resilient_llm`.
- `result = await chain.ainvoke({"input": text})`; en caso de excepcion, capturar `type(e).__name__` y el mensaje, e imprimir sin romper el programa (dejar espacio para un fallback u observabilidad futura).

### Pistas de la catedra

- `with_structured_output(ClasePydantic)` es mas robusto que parsear texto libre a mano.
- Para resiliencia: `.with_retry()` (fallos transitorios/red/rate limit) o `.with_fallbacks()` (cadena de respaldo alternativa).
- Pydantic lanza `ValidationError` si el LLM devuelve JSON valido pero con tipos/valores incorrectos — siempre envolver en `try/except`.

### Rubrica (100 pts, aprobacion 65 pts)

| Criterio | Descripcion | Peso |
|---|---|---|
| Integridad del contrato de datos (Pydantic) | Definicion de modelos Pydantic con validaciones semanticas y tipos correctos | 35% |
| Implementacion de structured output y LCEL | Integracion del esquema con `.with_structured_output()` dentro de la sintaxis LCEL | 25% |
| Estrategias de resiliencia (retries y fallbacks) | Manejo proactivo de errores de red o formato | 25% |
| Arquitectura y calidad de codigo | Legibilidad, modularidad, uso de Python 3.12 | 15% |

---

## 4. Componente C — Pre-entrega 2: "Pipeline de procesamiento validado"

Este es el entregable principal de la Fase 2 (el que pediste incorporar literalmente).

### Que construir

Un **Pipeline de Extraccion de Entidades Tecnicas**: recibe un parrafo de texto sin procesar (ej. descripcion de arquitectura de software o log de error) y devuelve un objeto validado.

Componentes requeridos:

1. **Esquema Pydantic**: campos `tecnologias` (lista de strings, no vacia), `nivel_de_criticidad` (enum: `baja`, `media`, `alta`), `resumen_tecnico` (string).
2. **Prompt Template**: modular, acepta el texto de entrada y las instrucciones de formato (`ChatPromptTemplate`, nunca f-strings sueltas).
3. **Cadena LCEL**: `prompt | model.with_structured_output(Schema)`.
4. **Logica de resiliencia**: al menos un reintento automatico (`.with_retry()`) si el LLM devuelve JSON mal formado o incompleto.

### Pasos sugeridos

1. Definir el contrato Pydantic con las restricciones de negocio (ej. lista de tecnologias no vacia → `Field(min_length=1)`).
2. Preparar el parser: `PydanticOutputParser` o (preferido) `.with_structured_output()`.
3. Ensamblar la cadena: `chain = prompt | model.with_structured_output(TuEsquema)`.
4. Añadir resiliencia con `.with_retry()`.
5. Prueba de estres: pasar un texto ambiguo y verificar si el validador lanza excepciones o el modelo se recupera.

### Errores comunes a evitar

- **Ignorar el `finish_reason`**: si el LLM corta la respuesta por falta de tokens, detectar que el objeto esta incompleto antes de intentar transformarlo.
- **Hardcoding de prompts**: nada de f-strings de Python dentro de la cadena; usar `ChatPromptTemplate` para que LangChain gestione las variables de entrada.

### Implementacion sugerida (checklist tecnico del enunciado)

1. `schemas.py`: estructura de salida deseada con Pydantic.
2. `chain.py`: cliente `ChatOpenAI`/`ChatAnthropic` (o el proveedor gratuito elegido, reutilizando la logica de carga de keys del Modulo 1).
3. `ChatPromptTemplate` que instruya al modelo a extraer informacion tecnica de un texto.
4. Cadena LCEL: `prompt | model.with_structured_output(Schema)`.
5. Funcion asincrona `process_text(text: str)` que ejecute la cadena con `.ainvoke()`.
6. Logs adecuados para observar el proceso de validacion y los reintentos.

### Ejemplo de salida esperada

```json
{
  "tecnologias": ["FastAPI", "Redis", "PostgreSQL"],
  "nivel_de_criticidad": "alta",
  "resumen_tecnico": "API con cache en Redis y persistencia en PostgreSQL; cuello de botella en conexiones concurrentes."
}
```

### Rubrica (100 pts, aprobacion 65 pts)

| Criterio | Descripcion | Peso |
|---|---|---|
| Definicion del esquema y salida estructurada | Uso de Pydantic para contratos de datos + `with_structured_output` | 30% |
| Implementacion de cadena LCEL y prompting | Sintaxis `\|` + diseño de `ChatPromptTemplate` para extraccion tecnica | 30% |
| Ejecucion asincrona y resiliencia | Uso de `.ainvoke()` + logs de flujo y validacion | 25% |
| Estructura del repositorio y script de prueba | Organizacion en modulos (`schemas.py`, `chain.py`) + script de prueba | 15% |

### Que entregar (formato)

- Tipo: **repositorio de GitHub**.
- Artefactos concretos: `schemas.py` (modelo Pydantic), `chain.py` (cadena LCEL con `.with_structured_output()` y `.with_retry()`), mini-script de prueba asincrono.
- **No hace falta PDF ni informe**: el ejemplo de salida JSON y las instrucciones de uso van en el `README.md`.

### Checklist de entrega (tal cual el enunciado)

- [ ] Repositorio de GitHub con `schemas.py` (modelo Pydantic) y `chain.py` (cadena LCEL).
- [ ] Cadena compuesta con LCEL: `prompt | model.with_structured_output(Schema)`.
- [ ] Logica de reintento (`.with_retry()`) ante JSON mal formado o incompleto.
- [ ] Funcion asincrona `process_text()` con `.ainvoke()` y logs de validacion.
- [ ] Mini-script de prueba que ejecute un ejemplo.

---

## 5. Requisitos transversales (heredados de la Fase 1 + especificos de LangChain)

1. **Python 3.12+**, todo asincrono real (`ainvoke`/`abatch`/`astream`, nunca bloqueante).
2. **Codigo en ingles** (nombres, comentarios, docstrings); **texto de cara al usuario en espanol sin tildes ni "ñ"** (logs, mensajes de error, prints).
3. Generar/actualizar **`.env`**, **`.env.example`** y **`.gitignore`** (mismas reglas que en la Fase 1).
4. **Preferir proveedores de IA gratuitos**: ver seccion 6. LangChain necesita el paquete "partner" del proveedor ademas de la API key.
5. Nunca usar f-strings crudas para armar prompts dentro de una cadena: siempre `ChatPromptTemplate`.
6. Todo llamado a un LLM dentro de una cadena de produccion debe tener manejo de resiliencia (`with_retry` como minimo).

---

## 6. Proveedores gratuitos con LangChain (verificado agosto 2026)

`with_structured_output()` — el metodo clave de esta fase — esta soportado en los dos proveedores gratuitos recomendados en la Fase 1:

| Proveedor | Paquete LangChain | Clase | Soporte `with_structured_output` | Notas |
|---|---|---|---|---|
| **Groq** | `langchain-groq` | `ChatGroq` | Si (via tool calling nativo) | Gratis, sin tarjeta. Ideal para Llama 3.1/3.3, Mixtral. |
| **Google Gemini** | `langchain-google-genai` | `ChatGoogleGenerativeAI` | Si (metodos `function_calling`, `json_mode`, `json_schema`; default `json_schema`) | Gratis, sin tarjeta. Cuidado: no combinar `with_structured_output(method="function_calling")` con otras tools (ej. Google Search) en la misma llamada. |
| OpenAI / Anthropic | `langchain-openai` / `langchain-anthropic` | `ChatOpenAI` / `ChatAnthropic` | Si | Solo si el usuario ya paga; no son gratis. |

**Sugerencia concreta**: usar `ChatGroq` o `ChatGoogleGenerativeAI` como modelo dentro de las cadenas LCEL de esta fase, exactamente igual que en la Fase 1. Instalar el paquete correspondiente (`pip install langchain-groq` o `pip install langchain-google-genai`) ademas de `langchain` y `langchain-core`.

---

## 7. Estructura de proyecto sugerida (extension de la Fase 1)

```
proyecto_ch_ai/
├── .env
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── entregable_a_orquestador/        # Fase 1
├── entregable_b_llm_client/         # Fase 1
├── fase2_lcel_refactor/
│   └── main.py                      # Componente A: refactorizacion a LCEL asincrono
├── fase2_ejercicio_validacion/
│   └── entity_extraction.py         # Componente B: ejercicio with_structured_output + with_retry
└── fase2_pipeline_validado/         # Componente C: Pre-entrega 2 (entregable principal)
    ├── schemas.py
    ├── chain.py
    ├── main.py                      # mini-script de prueba asincrono
    └── README.md
```

---

## 8. Checklist final antes de dar la Fase 2 por aprobada

- [ ] Componente A: cadena LCEL asincrona (`prompt | model | StrOutputParser`) ejecutada con `ainvoke`, sin logica imperativa en el flujo principal.
- [ ] Componente B: `EntityExtraction` con Pydantic + `with_structured_output` + `with_retry`, manejo de excepciones sin crash.
- [ ] Componente C (Pre-entrega 2): `schemas.py` + `chain.py` con el esquema `tecnologias`/`nivel_de_criticidad`/`resumen_tecnico`, cadena `prompt | model.with_structured_output(Schema)`, `.with_retry()`, `process_text()` asincrona con `.ainvoke()` y logs.
- [ ] Prueba de estres realizada con un texto ambiguo (documentar el resultado en el README).
- [ ] `.env` / `.env.example` / `.gitignore` actualizados.
- [ ] `README.md` del pipeline con el ejemplo de salida JSON y las instrucciones de uso (sin PDF/informe aparte).
- [ ] Codigo en ingles; mensajes al usuario en español sin tildes/ñ.
