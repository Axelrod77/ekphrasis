import json
import redis.asyncio as redis
from app.config import settings

_redis = None


async def get_redis():
    global _redis
    if _redis is None:
        _redis = redis.from_url(settings.redis_url)
    return _redis


async def get_cached(key: str) -> dict | None:
    r = await get_redis()
    data = await r.get(key)
    if data:
        return json.loads(data)
    return None


async def set_cached(key: str, value: dict, ttl_seconds: int = 900):
    r = await get_redis()
    await r.setex(key, ttl_seconds, json.dumps(value))
