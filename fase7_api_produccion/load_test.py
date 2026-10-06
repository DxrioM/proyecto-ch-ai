"""Fase 7: prueba de carga - 5 peticiones concurrentes contra la API real.

Requiere la API corriendo (uvicorn fase7_api_produccion.app.main:app).
Lanza 5 preguntas en simultaneo, espera a que cada una termine (polling
GET /tasks/{id}; si alguna queda AWAITING_APPROVAL por el gate HITL, la
aprueba automaticamente para no bloquear la corrida), y mide la latencia
real de cada una (incluida la p95 del lote).

Una de las 5 preguntas pide un calculo a proposito, para que la prueba de
carga tambien ejercite el camino de Human-in-the-loop bajo concurrencia.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Any, Dict

import httpx

BASE_URL = "http://127.0.0.1:8000"

PREGUNTAS = [
    "Cuantos pedidos tuvo el cliente 102 y cual fue el total?",
    "Que base de datos usa el sistema de pedidos para persistencia?",
    "Investiga los tiempos de respuesta comprometidos por severidad de soporte y calculame el promedio en horas.",
    "Que pasa si el health check de Kubernetes falla despues de un despliegue?",
    "Por que puede aparecer stock insuficiente en pedidos que si tienen stock?",
]

POLL_INTERVAL_SECONDS = 1.0
POLL_TIMEOUT_SECONDS = 600.0

RESULT_PATH = Path(__file__).parent / "metrics" / "load_test_resultado.json"


async def _esperar_resultado(client: httpx.AsyncClient, job_id: str) -> Dict[str, Any]:
    inicio = time.perf_counter()
    while time.perf_counter() - inicio < POLL_TIMEOUT_SECONDS:
        r = await client.get(f"{BASE_URL}/tasks/{job_id}")
        job = r.json()
        if job["status"] == "AWAITING_APPROVAL":
            await client.post(f"{BASE_URL}/tasks/{job_id}/approve", json={"aprobado": True})
        elif job["status"] in ("DONE", "FAILED", "REJECTED"):
            return job
        await asyncio.sleep(POLL_INTERVAL_SECONDS)
    raise TimeoutError(f"El job {job_id} no termino dentro de {POLL_TIMEOUT_SECONDS}s")


async def _correr_una(client: httpx.AsyncClient, pregunta: str) -> Dict[str, Any]:
    t0 = time.perf_counter()
    r = await client.post(f"{BASE_URL}/tasks", json={"pregunta": pregunta})
    r.raise_for_status()
    job_id = r.json()["job_id"]
    job_final = await _esperar_resultado(client, job_id)
    latencia = time.perf_counter() - t0
    return {
        "pregunta": pregunta,
        "job_id": job_id,
        "status": job_final["status"],
        "latencia_segundos": round(latencia, 3),
    }


def _percentil(valores_ordenados: list, p: float) -> float:
    if not valores_ordenados:
        return 0.0
    indice = min(len(valores_ordenados) - 1, int(round(p * (len(valores_ordenados) - 1))))
    return valores_ordenados[indice]


async def main() -> None:
    async with httpx.AsyncClient(timeout=POLL_TIMEOUT_SECONDS + 10) as client:
        t0 = time.perf_counter()
        resultados = await asyncio.gather(*[_correr_una(client, p) for p in PREGUNTAS])
        duracion_total = round(time.perf_counter() - t0, 3)

    latencias = sorted(r["latencia_segundos"] for r in resultados)

    resumen = {
        "cantidad_peticiones": len(resultados),
        "duracion_total_segundos": duracion_total,
        "latencia_p95_segundos": round(_percentil(latencias, 0.95), 3),
        "latencia_promedio_segundos": round(sum(latencias) / len(latencias), 3),
        "latencia_minima_segundos": latencias[0],
        "latencia_maxima_segundos": latencias[-1],
        "resultados": resultados,
    }

    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n5 peticiones concurrentes - duracion total: {duracion_total}s")
    print(f"Latencia p95: {resumen['latencia_p95_segundos']}s | promedio: {resumen['latencia_promedio_segundos']}s")
    for r in resultados:
        print(f"  [{r['status']}] {r['latencia_segundos']}s - {r['pregunta'][:70]}")
    print(f"\nResumen guardado en {RESULT_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
