"""Herramientas del agente: simulan operaciones sobre el Sistema de Pedidos
Online (mismo dominio ficticio usado en las Fases 3 y 4).

El LLM decide cuando usar cada una EXCLUSIVAMENTE en base al docstring, asi
que son deliberadamente descriptivas (que hace, cuando usarla, que
devuelve, como se relaciona con la otra herramienta).
"""

from langchain_core.tools import tool

from .data_store import PEDIDOS_POR_CLIENTE


@tool
def buscar_pedidos(cliente_id: int) -> dict:
    """Busca todos los pedidos de un cliente en el Sistema de Pedidos Online.

    Usa esta herramienta cuando el usuario pregunte cuantos pedidos tiene
    un cliente, cual es el monto total gastado, o pida un resumen general
    de sus compras. Recibe el ID numerico del cliente (ej. 102) y devuelve
    un resumen: cantidad de pedidos, monto total, y la lista de IDs de
    pedido (util para despues pedir el detalle de uno en particular con
    obtener_detalle_pedido, por ejemplo "el ultimo pedido" es el ultimo ID
    de esa lista). Si el cliente no existe, devuelve un campo "error"
    explicando que no se encontro, en vez de lanzar una excepcion.
    """
    pedidos = PEDIDOS_POR_CLIENTE.get(cliente_id)
    if pedidos is None:
        return {"error": f"No se encontro ningun cliente con ID {cliente_id}"}

    total = sum(p["monto"] for p in pedidos)
    return {
        "cliente_id": cliente_id,
        "pedidos": len(pedidos),
        "total": total,
        "pedido_ids": [p["id"] for p in pedidos],
    }


@tool
def obtener_detalle_pedido(pedido_id: int) -> dict:
    """Obtiene el detalle completo de un pedido especifico por su ID.

    Usa esta herramienta cuando el usuario pida detalles de un pedido en
    particular (ej. "el ultimo pedido", "el pedido 5003"): fecha, monto,
    estado del envio (entregado / en camino / cancelado) y los productos
    incluidos. Normalmente se usa DESPUES de buscar_pedidos, una vez que ya
    se tiene el ID del pedido de interes (buscar_pedidos devuelve
    "pedido_ids" con todos los IDs disponibles de ese cliente). Si el
    pedido no existe, devuelve un campo "error" en vez de lanzar una
    excepcion.
    """
    for pedidos in PEDIDOS_POR_CLIENTE.values():
        for pedido in pedidos:
            if pedido["id"] == pedido_id:
                return pedido
    return {"error": f"No se encontro ningun pedido con ID {pedido_id}"}
