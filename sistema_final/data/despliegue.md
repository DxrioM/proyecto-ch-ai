# Guia de Despliegue

Todos los microservicios se empaquetan como imagenes Docker independientes.
El pipeline de CI/CD (GitHub Actions) construye la imagen, corre los tests
automatizados y, si pasan, publica la imagen en el registry interno.

El despliegue en produccion se hace sobre un cluster de Kubernetes. Cada
microservicio tiene su propio Deployment y Service de Kubernetes, con
autoscaling horizontal basado en uso de CPU (HPA).

Antes de desplegar una version nueva a produccion, primero se despliega en
el ambiente de staging y se corre una bateria de pruebas de humo (smoke
tests) contra los endpoints criticos: creacion de pedido, consulta de
stock y confirmacion de pago.

El rollback ante un despliegue fallido es automatico: si el health check de
Kubernetes falla durante los primeros 5 minutos post-despliegue, el cluster
vuelve automaticamente a la version anterior de la imagen.
