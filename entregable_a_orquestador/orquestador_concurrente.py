"""Entregable A: Orquestador Concurrente de Modelos.

Simula la logica de un backend que consulta multiples fuentes de IA de forma
eficiente, sin llamar APIs reales (solo simula latencia con asyncio.sleep).

Demo 1: tres "modelos" corren en paralelo con asyncio.gather, la ejecucion
total esta acotada por asyncio.timeout(2.0).
Demo 2: 10 llamadas simuladas se lanzan a la vez pero un asyncio.Semaphore(2)
limita a 2 ejecuciones concurrentes.
"""

import asyncio
import logging
import random
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("orquestador")

INICIO_PROGRAMA = time.perf_counter()


def transcurrido() -> str:
    """Segundos transcurridos desde el arranque del programa, para logs legibles."""
    return f"t+{time.perf_counter() - INICIO_PROGRAMA:0.3f}s"


# ---------------------------------------------------------------------------
# Demo 1: gather + timeout sobre tres "modelos"
# ---------------------------------------------------------------------------

async def gpt_4_call(prompt: str) -> str:
    """Simula una llamada al modelo GPT-4 (latencia rapida)."""
    logger.info("[%s] gpt_4_call: inicio", transcurrido())
    await asyncio.sleep(1.0)
    logger.info("[%s] gpt_4_call: fin", transcurrido())
    return f"Respuesta de GPT-4 para: '{prompt}'"


async def claude_3_call(prompt: str) -> str:
    """Simula una llamada al modelo Claude 3 (latencia media)."""
    logger.info("[%s] claude_3_call: inicio", transcurrido())
    await asyncio.sleep(1.5)
    logger.info("[%s] claude_3_call: fin", transcurrido())
    return f"Respuesta de Claude 3 para: '{prompt}'"


async def local_llama_call(prompt: str) -> str:
    """Simula una llamada a un Llama local (latencia lenta, dispara el timeout)."""
    logger.info("[%s] local_llama_call: inicio", transcurrido())
    await asyncio.sleep(3.0)
    logger.info("[%s] local_llama_call: fin", transcurrido())
    return f"Respuesta de Llama local para: '{prompt}'"


async def orquestar_tres_modelos(prompt: str) -> None:
    """Dispara los tres modelos en simultaneo, acotado por un timeout global de 2s."""
    logger.info("--- Demo 1: gather + timeout(2.0) ---")
    try:
        async with asyncio.timeout(2.0):
            resultados = await asyncio.gather(
                gpt_4_call(prompt),
                claude_3_call(prompt),
                local_llama_call(prompt),
            )
        for resultado in resultados:
            logger.info("Resultado recibido: %s", resultado)
    except TimeoutError:
        logger.error(
            "[%s] Se agoto el tiempo de espera (2.0s): al menos un modelo tardo demasiado",
            transcurrido(),
        )
    logger.info("El programa sigue corriendo despues del timeout.\n")


# ---------------------------------------------------------------------------
# Demo 2: Semaphore limitando concurrencia sobre 10 llamadas
# ---------------------------------------------------------------------------

async def llamada_simulada(indice: int, semaforo: asyncio.Semaphore) -> str:
    """Simula una llamada generica a un modelo, respetando el limite del semaforo."""
    async with semaforo:
        logger.info("[%s] llamada #%d: adquiere el semaforo, inicio", transcurrido(), indice)
        duracion = random.uniform(0.3, 0.6)
        await asyncio.sleep(duracion)
        logger.info("[%s] llamada #%d: libera el semaforo, fin", transcurrido(), indice)
        return f"Resultado de la llamada #{indice}"


async def orquestar_con_semaforo(cantidad_llamadas: int = 10, limite_concurrente: int = 2) -> None:
    """Lanza N llamadas simuladas a la vez, pero solo `limite_concurrente` corren en paralelo."""
    logger.info("--- Demo 2: Semaphore(%d) sobre %d llamadas ---", limite_concurrente, cantidad_llamadas)
    semaforo = asyncio.Semaphore(limite_concurrente)
    tareas = [llamada_simulada(i, semaforo) for i in range(1, cantidad_llamadas + 1)]
    resultados = await asyncio.gather(*tareas)
    logger.info("Total de resultados recibidos: %d", len(resultados))


async def main() -> None:
    await orquestar_tres_modelos("Que es la entropia?")
    await orquestar_con_semaforo()


if __name__ == "__main__":
    asyncio.run(main())
