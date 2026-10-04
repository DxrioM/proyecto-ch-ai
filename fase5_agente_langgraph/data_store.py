"""Datos de ejemplo: simulan la base de datos del Sistema de Pedidos Online
(mismo dominio ficticio usado en las Fases 3 y 4), ahora consultados por un
agente en vez de recuperados via RAG.
"""

from typing import Any, Dict, List

PEDIDOS_POR_CLIENTE: Dict[int, List[Dict[str, Any]]] = {
    102: [
        {
            "id": 5001,
            "fecha": "2026-08-03",
            "monto": 4500.0,
            "estado": "entregado",
            "productos": ["Teclado mecanico", "Mouse inalambrico"],
        },
        {
            "id": 5002,
            "fecha": "2026-08-20",
            "monto": 6000.0,
            "estado": "entregado",
            "productos": ["Monitor 27 pulgadas"],
        },
        {
            "id": 5003,
            "fecha": "2026-09-15",
            "monto": 4000.0,
            "estado": "en camino",
            "productos": ["Silla ergonomica"],
        },
    ],
    205: [
        {
            "id": 5101,
            "fecha": "2026-07-11",
            "monto": 1200.0,
            "estado": "entregado",
            "productos": ["Cable HDMI"],
        },
        {
            "id": 5102,
            "fecha": "2026-09-02",
            "monto": 8900.0,
            "estado": "cancelado",
            "productos": ["Notebook 14 pulgadas"],
        },
    ],
    310: [
        {
            "id": 5201,
            "fecha": "2026-06-28",
            "monto": 15000.0,
            "estado": "entregado",
            "productos": ["Impresora laser", "Resma de papel"],
        },
    ],
}
