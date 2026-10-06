"""Fase 7: exporta metricas reales de LangSmith (costo por ejecucion +
latencia p95) para las ejecuciones de la prueba de carga, y las combina con
el resultado local de load_test.py en metrics/dashboard_data.json - la
fuente de datos del dashboard HTML dinamico (reemplaza las screenshots del
dashboard por datos reales, verificables y versionados).
"""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from langsmith import Client

LOAD_TEST_PATH = Path(__file__).parent / "metrics" / "load_test_resultado.json"
OUTPUT_PATH = Path(__file__).parent / "metrics" / "dashboard_data.json"
PROJECT_NAME = "proyecto-ch-ai-fase7"


def _percentil(valores_ordenados: list, p: float) -> float:
    if not valores_ordenados:
        return 0.0
    indice = min(len(valores_ordenados) - 1, int(round(p * (len(valores_ordenados) - 1))))
    return valores_ordenados[indice]


def main() -> None:
    load_dotenv()
    if not os.environ.get("LANGSMITH_API_KEY"):
        raise ValueError("Falta LANGSMITH_API_KEY en .env")
    if not LOAD_TEST_PATH.exists():
        raise ValueError(f"No se encontro {LOAD_TEST_PATH}. Corre load_test.py primero.")

    load_test = json.loads(LOAD_TEST_PATH.read_text(encoding="utf-8"))

    client = Client()
    # Ventana de la corrida de load_test.py: termino cuando se escribio el
    # archivo de resultados, y arranco duracion_total_segundos antes (con un
    # margen de 30s). Asi no mezclamos trazas de corridas anteriores.
    fin_ventana = datetime.fromtimestamp(LOAD_TEST_PATH.stat().st_mtime, tz=timezone.utc) + timedelta(seconds=30)
    inicio_ventana = fin_ventana - timedelta(seconds=load_test["duracion_total_segundos"] + 60)
    runs = [
        r
        for r in client.list_runs(project_name=PROJECT_NAME, is_root=True, start_time=inicio_ventana)
        if r.start_time and r.start_time <= fin_ventana
    ]

    ejecuciones = []
    for run in runs:
        latencia = None
        if run.end_time and run.start_time:
            latencia = (run.end_time - run.start_time).total_seconds()
        ejecuciones.append(
            {
                "run_id": str(run.id),
                "nombre": run.name,
                "latencia_segundos": latencia,
                "total_tokens": run.total_tokens,
                "prompt_tokens": run.prompt_tokens,
                "completion_tokens": run.completion_tokens,
                "total_cost_usd": float(run.total_cost) if run.total_cost is not None else None,
            }
        )

    latencias = sorted(e["latencia_segundos"] for e in ejecuciones if e["latencia_segundos"] is not None)
    costos = [e["total_cost_usd"] for e in ejecuciones if e["total_cost_usd"] is not None]

    resumen = {
        "generado_en": datetime.now(timezone.utc).isoformat(),
        "proyecto_langsmith": PROJECT_NAME,
        "cantidad_ejecuciones_encontradas": len(ejecuciones),
        "latencia_p95_segundos_langsmith": round(_percentil(latencias, 0.95), 3) if latencias else None,
        "costo_total_usd": round(sum(costos), 6) if costos else None,
        "costo_promedio_por_ejecucion_usd": round(sum(costos) / len(costos), 6) if costos else None,
        "nota_costo": (
            None
            if costos
            else (
                "LangSmith no devolvio costo (total_cost) para estas ejecuciones - "
                "probablemente porque no tiene una tabla de precios configurada "
                "para el modelo de Groq usado (no es un proveedor con precios "
                "incorporados por defecto). Los conteos de tokens "
                "(prompt_tokens/completion_tokens) si estan disponibles, y son la "
                "base para calcular el costo manualmente con el precio publicado "
                "por Groq."
            )
        ),
        "ejecuciones": ejecuciones,
        "prueba_de_carga_local": load_test,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(resumen, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    print(f"Metricas de LangSmith exportadas a {OUTPUT_PATH}")
    print(f"Ejecuciones encontradas: {len(ejecuciones)}")
    print(f"Costo total: {resumen['costo_total_usd']}")
    print(f"Latencia p95 (LangSmith): {resumen['latencia_p95_segundos_langsmith']}")


if __name__ == "__main__":
    main()
