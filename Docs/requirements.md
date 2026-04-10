# Requerimientos del Sistema

## Requerimientos funcionales

| ID | Requerimiento | Estado |
|----|--------------|--------|
| RF-01 | La API debe exponer un endpoint `GET /inventory/{productId}` que retorne datos de un producto | ✅ |
| RF-02 | La API debe exponer un endpoint `GET /orders/{orderId}` que retorne datos de una orden | ✅ |
| RF-03 | Los endpoints de consulta deben usar Redis como cache | ✅ |
| RF-04 | Si el dato está en cache, responder desde Redis sin consultar la DB | ✅ |
| RF-05 | Si el dato no está en cache, consultar la DB y guardarlo en Redis con TTL | ✅ |
| RF-06 | La respuesta debe indicar si el dato provino de cache o de la base de datos | ✅ |
| RF-07 | Debe existir un endpoint para consultar el estado del cache (`/cache/stats`) | ✅ |
| RF-08 | Debe existir un endpoint para invalidar claves del cache (`DELETE /cache/{key}`) | ✅ |
| RF-09 | La API debe exponer un endpoint de salud (`/health`) que verifique la conexión a Redis | ✅ |

## Requerimientos no funcionales

| ID | Requerimiento | Valor |
|----|--------------|-------|
| RNF-01 | Toda clave en Redis debe tener TTL | 30 segundos |
| RNF-02 | El sistema debe levantarse con un solo comando | `docker compose up --build` |
| RNF-03 | Redis debe estar saludable antes de iniciar la API | Healthcheck en Docker Compose |
| RNF-04 | Redis no debe usar memoria ilimitada | Límite: 128MB, política: allkeys-lru |
| RNF-05 | La API debe indicar latencia de origen en la respuesta | Campo `source` en JSON |

## Requerimientos de infraestructura

| Requerimiento | Implementación |
|--------------|---------------|
| API en contenedor Docker | `Dockerfile` en `/app` |
| Redis en contenedor Docker | Imagen oficial `redis:7.2-alpine` |
| Orquestación multi-contenedor | `docker-compose.yml` con red interna |
| Comunicación entre contenedores | Red Docker `apicache_default` |
| Persistencia de Redis | Volumen Docker `redis_data` |

## Dependencias técnicas

```
fastapi==0.111.0
uvicorn==0.29.0
redis==5.0.4
Python 3.11
Docker Engine 20+
Docker Compose v3.9+
```

## Requisitos para ejecutar localmente

- Docker Desktop instalado y corriendo
- Puerto 8000 disponible (API)
- Puerto 6379 disponible (Redis)
- Conexión a internet (primera vez, para descargar imágenes)
