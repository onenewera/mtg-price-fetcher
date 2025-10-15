import os
import json
import time
import logging
from typing import Any, Optional

try:
    import redis as _redis
except Exception:  # pragma: no cover - optional dependency at runtime
    _redis = None

logger = logging.getLogger(__name__)


class RedisCache:
    def __init__(self, url: str, default_ttl_seconds: int = 600) -> None:
        if _redis is None:
            raise RuntimeError("redis package not available")
        self.client = _redis.from_url(url)
        self.default_ttl_seconds = default_ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        try:
            raw = self.client.get(key)
            if raw is None:
                return None
            return json.loads(raw)
        except Exception:
            logger.exception("Redis get failed")
            return None

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        try:
            ttl = ttl_seconds or self.default_ttl_seconds
            self.client.setex(key, ttl, json.dumps(value))
        except Exception:
            logger.exception("Redis set failed")


def get_redis_cache() -> Optional[RedisCache]:
    url = os.getenv("REDIS_URL")
    if not url:
        return None
    try:
        return RedisCache(url)
    except Exception:
        logger.exception("Failed to initialize Redis cache")
        return None


