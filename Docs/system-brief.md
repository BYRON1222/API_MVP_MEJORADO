# System Brief — API de Inventario con Cache Redis

## Nombre del sistema
**API Cache Inventario** — Sistema de consulta de inventario con cache Redis y TTL automático.

## Problema que resuelve
En sistemas de inventario con alto volumen de consultas, cada solicitud impacta directamente la base de datos, generando latencia acumulada y carga innecesaria. Este MVP implementa una capa de cache con Redis que intercepta las consultas repetidas y responde desde memoria, reduciendo el tiempo de respuesta de ~300ms a ~1ms en cache hits.

## MVP — Resumen

El sistema expone una API REST construida con FastAPI que permite consultar productos y órdenes. Los endpoints de lectura implementan el patrón **cache-aside con TTL** usando Redis:

- Primera consulta → base de datos (lenta)
- Consultas siguientes dentro del TTL → Redis (rápida)
- Al expirar el TTL → ciclo se reinicia automáticamente

## Componentes principales

| Componente | Descripción |
|-----------|-------------|
| `fastapi_app` | API REST con 5 endpoints, corre en puerto 8000 |
| `redis_cache` | Instancia Redis 7.2, corre en puerto 6379 |
| Docker Compose | Orquesta ambos contenedores con red interna y healthcheck |

## Endpoints del sistema

| Método | Endpoint | Cache |
|--------|----------|-------|
| GET | `/inventory/{productId}` | ✅ Redis TTL 30s |
| GET | `/orders/{orderId}` | ✅ Redis TTL 30s |
| GET | `/cache/stats` | — |
| DELETE | `/cache/{key}` | — |
| GET | `/health` | — |
| GET | `/docs` | — Swagger UI |
