# Documentación de Cache con Redis

## 1. Endpoints que usan cache

| Endpoint | Descripción |
|----------|-------------|
| `GET /inventory/{productId}` | Consulta datos de un producto del inventario |
| `GET /orders/{orderId}` | Consulta datos de una orden por ID |

---

## 2. Claves de Redis generadas

| Endpoint | Clave Redis | Ejemplo |
|----------|-------------|---------|
| `/inventory/{productId}` | `inventory:{productId}` | `inventory:P001` |
| `/orders/{orderId}` | `order:{orderId}` | `order:O001` |

Las claves siguen el patrón `recurso:id` para evitar colisiones entre distintos tipos de datos.

---

## 3. TTL definido

**TTL: 30 segundos** para todos los endpoints cacheados.

Se eligió 30 segundos porque:
- Los datos de inventario y órdenes son semi-estáticos (no cambian en milisegundos)
- Es suficiente para absorber ráfagas de tráfico sobre el mismo recurso
- Evita datos muy desactualizados (stale data) en un sistema de inventario real
- Redis libera la memoria automáticamente sin intervención manual

---

## 4. Estrategia de cache: Cache-Aside (Lazy Loading)

La API implementa el patrón **cache-aside**, también llamado *lazy loading*:

1. La aplicación consulta Redis primero
2. Si la clave existe → retorna el dato desde cache (**cache hit**)
3. Si la clave no existe → consulta la fuente principal, almacena el resultado en Redis con TTL, y retorna el dato (**cache miss**)

Redis **no** carga datos proactivamente; solo guarda lo que la aplicación le pide guardar.

---

## 5. Comportamiento: Cache Hit vs Cache Miss

### Cache Hit
```
Cliente → GET /inventory/P001
API     → Redis: GET inventory:P001  →  [dato encontrado]
API     → Responde con { "source": "cache", "ttl_remaining_seconds": 24, ... }
```
- Tiempo de respuesta: ~1ms (sin latencia de DB)
- No se consulta la base de datos

### Cache Miss
```
Cliente → GET /inventory/P001
API     → Redis: GET inventory:P001  →  [nil, no existe]
API     → Consulta base de datos     →  [dato obtenido, ~300ms]
API     → Redis: SETEX inventory:P001 30 {dato}
API     → Responde con { "source": "database", "ttl_remaining_seconds": 30, ... }
```
- Tiempo de respuesta: ~300ms (latencia real de DB)
- El dato queda cacheado para las próximas 30 segundas

---

## 6. Riesgos y limitaciones

| Riesgo | Descripción | Mitigación |
|--------|-------------|------------|
| **Stale data** | El inventario puede cambiar durante los 30s de TTL | TTL corto; invalidación manual disponible vía `DELETE /cache/{key}` |
| **Cache stampede** | Muchas solicitudes simultáneas en cache miss pueden saturar la DB | En producción usar mutex/lock o probabilistic early expiration |
| **Sin persistencia** | Redis en modo default no persiste en disco; un reinicio vacía el cache | Aceptable para cache; datos originales siempre en la DB |
| **Un solo nodo Redis** | No hay replicación ni clustering | Suficiente para MVP; en producción usar Redis Sentinel o Cluster |
| **Claves sin prefijo de entorno** | Las claves no distinguen entre dev/prod | En producción agregar prefijo: `prod:inventory:P001` |
