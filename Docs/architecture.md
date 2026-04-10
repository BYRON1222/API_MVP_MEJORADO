# Arquitectura del Sistema

## Diagrama de Arquitectura

```mermaid
graph TD
    Cliente["🖥️ Cliente\n(Browser / curl)"]
    API["🐍 FastAPI\nfastapi_app:8000"]
    Redis["⚡ Redis Cache\nredis_cache:6379"]
    DB["🗄️ Base de Datos\n(simulada en memoria)"]

    Cliente -->|"HTTP GET /inventory/{id}"| API
    API -->|"1. Buscar clave en cache"| Redis
    Redis -->|"2a. Cache HIT → retorna dato"| API
    Redis -->|"2b. Cache MISS → nil"| API
    API -->|"3. MISS: consultar DB"| DB
    DB -->|"4. Retorna dato"| API
    API -->|"5. SETEX con TTL=30s"| Redis
    API -->|"6. Responde al cliente"| Cliente

    style Redis fill:#DC382C,color:#fff
    style API fill:#009688,color:#fff
    style Cliente fill:#1565C0,color:#fff
    style DB fill:#5D4037,color:#fff
```

---

## Diagrama de Flujo del Cache

```mermaid
flowchart TD
    A([Solicitud GET /inventory/id]) --> B{¿Existe clave\nen Redis?}
    B -->|Sí - Cache HIT| C[Leer dato de Redis]
    B -->|No - Cache MISS| D[Consultar base de datos]
    C --> E[Responder: source=cache\ncon TTL restante]
    D --> F[Guardar en Redis\nSETEX TTL=30s]
    F --> G[Responder: source=database\nTTL=30]

    style B fill:#FFA000,color:#000
    style C fill:#DC382C,color:#fff
    style D fill:#5D4037,color:#fff
    style F fill:#DC382C,color:#fff
```

---

## Contenedores Docker

```mermaid
graph LR
    subgraph Docker Compose Network: apicache_default
        A["fastapi_app\nPuerto: 8000\nImagen: build ./app"]
        B["redis_cache\nPuerto: 6379\nImagen: redis:7.2-alpine"]
    end
    Host["Host Machine"] -->|"localhost:8000"| A
    A -->|"redis:6379"| B

    style A fill:#009688,color:#fff
    style B fill:#DC382C,color:#fff
```

---

## Dónde entra Redis en la arquitectura

Redis se ubica entre la API y la base de datos como una **capa de cache intermedia**. Cada vez que llega una solicitud a la API, Redis es el primer punto de consulta. Solo si Redis no tiene el dato (cache miss) se accede a la fuente de datos principal.

```
Cliente → API → Redis → (si miss) → DB
```

---

## Responsabilidad de Redis en el sistema

| Responsabilidad | Detalle |
|----------------|---------|
| **Almacenamiento temporal** | Guarda respuestas de endpoints con TTL automático de 30 segundos |
| **Reducción de latencia** | Responde en ~1ms vs ~300ms de la DB |
| **Reducción de carga** | Evita consultas repetidas a la fuente de datos principal |
| **Gestión de memoria** | Configurado con `maxmemory 128mb` y política `allkeys-lru` para evitar desbordamiento |
| **Health check** | Docker Compose verifica que Redis responda antes de iniciar la API |

---

## Stack tecnológico

| Componente | Tecnología | Versión |
|-----------|-----------|---------|
| API | FastAPI + Uvicorn | 0.111.0 |
| Cliente Redis | redis-py | 5.0.4 |
| Cache | Redis Alpine | 7.2 |
| Lenguaje | Python | 3.11 |
| Orquestación | Docker Compose | v3.9 |
