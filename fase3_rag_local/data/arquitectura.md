# Arquitectura del Sistema de Pedidos Online

El backend expone una API REST construida con FastAPI (Python 3.12). La
persistencia principal de pedidos, clientes y productos se hace en
PostgreSQL 16. Para el cache de sesiones de usuario y el carrito de compras
se usa Redis.

La comunicacion asincrona entre servicios (por ejemplo, notificar al
servicio de facturacion cuando se confirma un pedido) se hace mediante una
cola de mensajes RabbitMQ.

El sistema esta dividido en tres microservicios independientes:

1. Servicio de Catalogo: expone productos y stock disponible.
2. Servicio de Pedidos: gestiona el ciclo de vida de un pedido (creado,
   pagado, enviado, entregado, cancelado).
3. Servicio de Notificaciones: envia emails y notificaciones push cuando
   cambia el estado de un pedido.

Cada microservicio tiene su propia base de datos logica dentro del mismo
cluster de PostgreSQL, siguiendo el patron database-per-service a nivel de
esquema.
