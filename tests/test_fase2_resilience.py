"""Tests sinteticos de resiliencia para la Fase 2 (LangChain / LCEL).

No llaman a la API real de Groq: inyectan un Runnable falso (RunnableLambda)
en lugar del ChatGroq real, envuelto en el .with_retry() REAL de LangChain
(con tiempos de espera reducidos via exponential_jitter_params, solo para
que el test suite corra rapido). Esto prueba el mecanismo de resiliencia de
verdad, no una reimplementacion casera.

Casos cubiertos por componente (B y C):
1. El modelo falla N veces (fallo transitorio de red) y se recupera antes de
   agotar los intentos -> la cadena debe devolver el resultado final.
2. El modelo falla siempre -> with_retry agota los intentos y la excepcion
   queda contenida (la funcion devuelve None, no crashea).
3. El modelo devuelve datos que no validan contra el esquema Pydantic
   (ValidationError) -> tambien queda contenida, sin crashear.
"""

import asyncio

from langchain_core.runnables import RunnableLambda
from pydantic import ValidationError

from fase2_ejercicio_validacion.entity_extraction import EntityExtraction, run_validated_chain
from fase2_pipeline_validado.chain import process_text
from fase2_pipeline_validado.schemas import NivelCriticidad, TechExtraction

# Backoff minimo para que los tests no esperen los varios segundos del
# backoff exponencial por defecto; siguen pasando por el with_retry() real.
FAST_RETRY = {"initial": 0.01, "max": 0.05}

TECH_OK = TechExtraction(
    tecnologias=["FastAPI"],
    nivel_de_criticidad=NivelCriticidad.MEDIA,
    resumen_tecnico="Texto de prueba",
)

ENTITY_OK = EntityExtraction(topic="tema de prueba", entities=["a", "b"], sentiment_score=0.5)


def _fake_runnable(action):
    """Runnable falso que ejecuta action() en cada llamada (via ainvoke).

    action() decide el comportamiento: puede devolver un valor, o lanzar una
    excepcion (de red o de validacion Pydantic) para simular un fallo.
    Devuelve (runnable, calls) donde calls['count'] cuenta las invocaciones.
    """
    calls = {"count": 0}

    async def _ainvoke(_input):
        calls["count"] += 1
        return action()

    return RunnableLambda(_ainvoke), calls


def _recovers_after(fail_times: int, success_value):
    """action() que falla las primeras `fail_times` veces (ConnectionError)
    y despues devuelve success_value."""
    state = {"n": 0}

    def action():
        state["n"] += 1
        if state["n"] <= fail_times:
            raise ConnectionError("fallo transitorio de red simulado")
        return success_value

    return action


def _always_fails_with_network_error():
    def action():
        raise ConnectionError("caido a proposito, nunca se recupera")

    return action


# ---------------------------------------------------------------------------
# Componente C: fase2_pipeline_validado.chain.process_text (TechExtraction)
# ---------------------------------------------------------------------------


def test_process_text_retries_and_recovers():
    """Falla 2 veces por red y responde bien al 3er intento: with_retry debe
    reintentar y process_text debe devolver el resultado, no None."""
    fake, calls = _fake_runnable(_recovers_after(fail_times=2, success_value=TECH_OK))
    resilient = fake.with_retry(stop_after_attempt=3, exponential_jitter_params=FAST_RETRY)

    resultado = asyncio.run(process_text("cualquier texto", resilient_model=resilient))

    assert resultado == TECH_OK
    assert calls["count"] == 3  # 2 fallos + 1 exito


def test_process_text_retry_exhausted_returns_none_without_crash():
    """El modelo falla siempre: with_retry agota los 3 intentos y process_text
    debe devolver None sin dejar escapar la excepcion."""
    fake, calls = _fake_runnable(_always_fails_with_network_error())
    resilient = fake.with_retry(stop_after_attempt=3, exponential_jitter_params=FAST_RETRY)

    resultado = asyncio.run(process_text("cualquier texto", resilient_model=resilient))

    assert resultado is None
    assert calls["count"] == 3


def test_process_text_validation_error_is_contained():
    """El LLM devuelve una lista de tecnologias vacia (viola min_length=1 de
    TechExtraction): la ValidationError de Pydantic debe quedar contenida,
    process_text no debe crashear."""

    def action():
        # Construir el modelo con datos invalidos dispara ValidationError,
        # igual que lo haria with_structured_output() puertas adentro.
        return TechExtraction(tecnologias=[], nivel_de_criticidad="alta", resumen_tecnico="x")

    fake, calls = _fake_runnable(action)
    resilient = fake.with_retry(
        stop_after_attempt=2,
        retry_if_exception_type=(ValidationError,),
        exponential_jitter_params=FAST_RETRY,
    )

    resultado = asyncio.run(process_text("texto ambiguo", resilient_model=resilient))

    assert resultado is None
    assert calls["count"] == 2


# ---------------------------------------------------------------------------
# Componente B: fase2_ejercicio_validacion.entity_extraction.run_validated_chain
# ---------------------------------------------------------------------------


def test_run_validated_chain_retries_and_recovers():
    fake, calls = _fake_runnable(_recovers_after(fail_times=2, success_value=ENTITY_OK))
    resilient = fake.with_retry(stop_after_attempt=3, exponential_jitter_params=FAST_RETRY)

    resultado = asyncio.run(run_validated_chain("cualquier texto", resilient_llm=resilient))

    assert resultado == ENTITY_OK
    assert calls["count"] == 3


def test_run_validated_chain_retry_exhausted_returns_none_without_crash():
    fake, calls = _fake_runnable(_always_fails_with_network_error())
    resilient = fake.with_retry(stop_after_attempt=3, exponential_jitter_params=FAST_RETRY)

    resultado = asyncio.run(run_validated_chain("cualquier texto", resilient_llm=resilient))

    assert resultado is None
    assert calls["count"] == 3


def test_run_validated_chain_validation_error_is_contained():
    """sentiment_score fuera de rango (debe estar entre 0 y 1) viola el
    esquema EntityExtraction."""

    def action():
        return EntityExtraction(topic="x", entities=["y"], sentiment_score=5.0)

    fake, calls = _fake_runnable(action)
    resilient = fake.with_retry(
        stop_after_attempt=2,
        retry_if_exception_type=(ValidationError,),
        exponential_jitter_params=FAST_RETRY,
    )

    resultado = asyncio.run(run_validated_chain("texto ambiguo", resilient_llm=resilient))

    assert resultado is None
    assert calls["count"] == 2
