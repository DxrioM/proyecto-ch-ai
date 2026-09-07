# Guia de Troubleshooting

## Error: "stock insuficiente" en pedidos que si tienen stock

Suele deberse a un desfasaje de cache: el Servicio de Catalogo cachea el
stock en Redis por 30 segundos. Si el stock cambio muy recientemente, puede
verse un valor viejo. Solucion: invalidar manualmente la clave de cache
stock:id_producto o esperar el TTL.

## Error: pedidos que quedan en estado "pagado" y nunca pasan a "enviado"

Generalmente indica que un mensaje se perdio en la cola RabbitMQ entre el
Servicio de Pedidos y el Servicio de Notificaciones, o que el consumidor
del Servicio de Notificaciones esta caido. Revisar el dashboard de
RabbitMQ: si hay mensajes acumulados en la cola pedidos.confirmados sin
consumir, reiniciar el pod del Servicio de Notificaciones.

## Error: latencia alta en el endpoint de busqueda de productos

Casi siempre es un problema de indices faltantes en PostgreSQL sobre la
tabla de productos, especialmente despues de agregar un filtro nuevo en el
frontend. Revisar el plan de ejecucion con EXPLAIN ANALYZE antes de asumir
que es un problema de infraestructura.
