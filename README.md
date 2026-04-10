# API con Cache Redis 🚀

Sistema de inventario con cache real usando FastAPI + Redis + Docker Compose.

## Estructura del proyecto

```
proyecto/
├── app/
│   ├── main.py           # API FastAPI
│   ├── requirements.txt  # Dependencias Python
│   └── Dockerfile        # Imagen del contenedor API
├── docker-compose.yml    # Orquestación de servicios
└── README.md
```

## Levantar el entorno

```bash
docker-compose up --build
```

La API estará disponible en: http://localhost:8000  
Documentación interactiva: http://localhost:8000/docs

---

## Endpoints disponibles

### `GET /inventory/{productId}`  ← **Endpoint con cache Redis + TTL**

Obtiene datos de un producto del inventario.

**Lógica de cache:**
1. Busca la clave `inventory:{productId}` en Redis
2. Si existe → responde desde cache (`"source": "cache"`)
3. Si no existe → consulta la base de datos, guarda en Redis con **TTL = 30 segundos**, responde desde DB

**IDs de prueba:** `P001`, `P002`, `P003`, `P004`, `P005`

```bash
curl http://localhost:8000/inventory/P001
```

**Primera llamada** (sin cache):
```json
{
  "source": "database",
  "ttl_remaining_seconds": 30,
  "data": { "id": "P001", "name": "Laptop Pro X", "stock": 45, "price": 1299.99 }
}
```

**Segunda llamada** (con cache):
```json
{
  "source": "cache",
  "ttl_remaining_seconds": 27,
  "data": { "id": "P001", "name": "Laptop Pro X", "stock": 45, "price": 1299.99 }
}
```

---

### `GET /orders/{orderId}`  ← **Endpoint con cache Redis + TTL**

Obtiene una orden por ID. Misma lógica de cache.

**IDs de prueba:** `O001`, `O002`, `O003`

```bash
curl http://localhost:8000/orders/O001
```

---

### `GET /cache/stats`

Muestra todas las claves actualmente en Redis con su TTL restante.

```bash
curl http://localhost:8000/cache/stats
```

---

### `DELETE /cache/{key}`

Invalida una clave del cache manualmente.

```bash
curl -X DELETE http://localhost:8000/cache/inventory:P001
```

---

### `GET /health`

Verifica el estado de la API y la conexión a Redis.

---

## ¿Por qué este endpoint para cache?

`GET /inventory/{productId}` es ideal para cache porque:

- Los datos de inventario **no cambian en milisegundos** — un TTL de 30 segundos es aceptable
- Es un endpoint de **alta frecuencia de lectura** (muchos clientes consultan stock)
- La consulta a DB simula **latencia real** (300ms) — el cache la elimina completamente
- El patrón **cache-aside** (read-through manual) es el más adecuado para inventario

## TTL elegido: 30 segundos

| Razón | Detalle |
|-------|---------|
| Datos semi-estáticos | El stock no cambia cada segundo |
| Balance freshness/performance | 30s evita stale data grave |
| Expiración automática | Redis libera memoria sin intervención |

## Verificar Redis manualmente

```bash
# Acceder al contenedor Redis
docker exec -it redis_cache redis-cli

# Ver todas las claves
KEYS *

# Ver TTL de una clave
TTL inventory:P001

# Ver valor de una clave
GET inventory:P001
```
