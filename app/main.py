from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import redis
import json
import time
import random
from datetime import datetime

app = FastAPI(
    title="API con Cache Redis",
    description="API de inventario con cache Redis y TTL",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conexión a Redis
r = redis.Redis(host="redis", port=6379, decode_responses=True)

CACHE_TTL = 30  # segundos

# Base de datos simulada de productos
PRODUCTS_DB = {
    "P001": {"id": "P001", "name": "Laptop Pro X", "stock": 45, "price": 1299.99, "category": "Electronics"},
    "P002": {"id": "P002", "name": "Wireless Mouse", "stock": 120, "price": 29.99, "category": "Accessories"},
    "P003": {"id": "P003", "name": "USB-C Hub", "stock": 78, "price": 49.99, "category": "Accessories"},
    "P004": {"id": "P004", "name": "Monitor 4K", "stock": 23, "price": 599.99, "category": "Electronics"},
    "P005": {"id": "P005", "name": "Mechanical Keyboard", "stock": 60, "price": 89.99, "category": "Accessories"},
}

ORDERS_DB = {
    "O001": {"id": "O001", "product": "P001", "qty": 2, "status": "shipped", "total": 2599.98},
    "O002": {"id": "O002", "product": "P003", "qty": 5, "status": "pending", "total": 249.95},
    "O003": {"id": "O003", "product": "P005", "qty": 1, "status": "delivered", "total": 89.99},
}


@app.get("/")
def root():
    return {
        "service": "API con Cache Redis",
        "version": "1.0.0",
        "endpoints": [
            "GET /inventory/{productId}",
            "GET /orders/{orderId}",
            "GET /cache/stats",
            "DELETE /cache/{key}",
        ]
    }


@app.get("/health")
def health():
    try:
        r.ping()
        redis_status = "connected"
    except Exception:
        redis_status = "disconnected"
    return {"status": "ok", "redis": redis_status, "timestamp": datetime.utcnow().isoformat()}


# ─── ENDPOINT CON CACHE REAL ───────────────────────────────────────────────────
@app.get("/inventory/{productId}")
def get_inventory(productId: str):
    cache_key = f"inventory:{productId}"

    # 1. Intentar obtener desde cache
    cached = r.get(cache_key)
    if cached:
        data = json.loads(cached)
        ttl_remaining = r.ttl(cache_key)
        return {
            "source": "cache",
            "ttl_remaining_seconds": ttl_remaining,
            "data": data
        }

    # 2. Si no está en cache, buscar en "base de datos"
    time.sleep(0.3)  # Simula latencia de DB
    product = PRODUCTS_DB.get(productId)
    if not product:
        raise HTTPException(status_code=404, detail=f"Producto '{productId}' no encontrado")

    # 3. Guardar en Redis con TTL obligatorio
    r.setex(cache_key, CACHE_TTL, json.dumps(product))

    return {
        "source": "database",
        "ttl_remaining_seconds": CACHE_TTL,
        "data": product
    }


@app.get("/orders/{orderId}")
def get_order(orderId: str):
    cache_key = f"order:{orderId}"

    cached = r.get(cache_key)
    if cached:
        data = json.loads(cached)
        return {
            "source": "cache",
            "ttl_remaining_seconds": r.ttl(cache_key),
            "data": data
        }

    time.sleep(0.2)
    order = ORDERS_DB.get(orderId)
    if not order:
        raise HTTPException(status_code=404, detail=f"Orden '{orderId}' no encontrada")

    r.setex(cache_key, CACHE_TTL, json.dumps(order))

    return {
        "source": "database",
        "ttl_remaining_seconds": CACHE_TTL,
        "data": order
    }


@app.get("/cache/stats")
def cache_stats():
    keys = r.keys("*")
    details = []
    for key in keys:
        ttl = r.ttl(key)
        val = r.get(key)
        details.append({
            "key": key,
            "ttl_seconds": ttl,
            "value_preview": val[:80] + "..." if val and len(val) > 80 else val
        })
    return {
        "total_cached_keys": len(keys),
        "cache_ttl_config": CACHE_TTL,
        "entries": details
    }


@app.delete("/cache/{key}")
def invalidate_cache(key: str):
    full_key = key
    deleted = r.delete(full_key)
    return {"deleted": bool(deleted), "key": full_key}
