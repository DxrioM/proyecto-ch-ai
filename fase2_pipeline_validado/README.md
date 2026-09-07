# Pipeline de Extraccion de Entidades Tecnicas (Pre-entrega 2)

Recibe un parrafo de texto sin procesar (descripcion de arquitectura de
software, log de error, etc.) y devuelve un objeto validado con las
tecnologias mencionadas, el nivel de criticidad y un resumen tecnico.

## Arquitectura

- `schemas.py`: `TechExtraction` (Pydantic) — `tecnologias` (lista no vacia),
  `nivel_de_criticidad` (enum `baja`/`media`/`alta`), `resumen_tecnico`.
- `chain.py`: cadena LCEL `prompt | model.with_structured_output(TechExtraction)`
  con `ChatGroq` (gratis, sin tarjeta) y `.with_retry()` para resiliencia ante
  fallos de red o JSON invalido. Expone `process_text(text)` asincrona.
- `main.py`: mini-script de prueba que corre un caso normal y una prueba de
  estres con texto ambiguo.

## Uso

Requiere `GROQ_API_KEY` en el `.env` de la raiz del proyecto (ver
`README.md` general).

```bash
python -m fase2_pipeline_validado.main
```

O usando `process_text` directamente:

```python
from fase2_pipeline_validado.chain import process_text

resultado = await process_text("El backend usa FastAPI, Redis y PostgreSQL...")
```

## Ejemplo de salida

Entrada:

> "El backend expone una API con FastAPI. Usamos Redis como cache de
> sesiones y PostgreSQL para persistencia. Bajo carga concurrente alta
> detectamos un cuello de botella en el pool de conexiones a la base de
> datos, lo que degrada el tiempo de respuesta de forma notoria."

Salida (`TechExtraction`, validada con Pydantic):

```json
{
  "tecnologias": ["FastAPI", "Redis", "PostgreSQL"],
  "nivel_de_criticidad": "alta",
  "resumen_tecnico": "Bottleneck en el pool de conexiones de PostgreSQL bajo alta concurrencia, afecta tiempos de respuesta de la API FastAPI."
}
```

## Prueba de estres

Se probo el pipeline con un texto deliberadamente ambiguo, sin nombrar
ninguna tecnologia especifica: *"El sistema anduvo raro ayer, capaz que fue
cosa de red."*

Resultado observado: el modelo **no fallo la validacion** — infirio una
tecnologia razonable a partir del contexto ("Networking") y devolvio un
`TechExtraction` valido con criticidad `baja`, en vez de lanzar una
`ValidationError` por lista vacia. Esto confirma que el prompt guia
correctamente al modelo para que siempre intente completar el esquema
(`tecnologias` con `min_length=1`) en vez de dejarlo incompleto; el
`.with_retry()` esta disponible como red de resguardo para los casos en los
que el modelo si devuelva algo invalido o falle la conexion.

## Resiliencia

`process_text()` nunca deja escapar una excepcion: si `.with_retry()` agota
sus 3 intentos (por un error de red/rate limit persistente, o porque el LLM
sigue devolviendo un JSON que no valida contra `TechExtraction`), la funcion
loggea el error (`type(e).__name__` + mensaje) y devuelve `None`, dejando que
el llamador decida el siguiente paso (reintento manual, fallback, alerta).
