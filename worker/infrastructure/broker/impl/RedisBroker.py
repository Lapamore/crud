import redis
from ..core import IBroker

__all__ = ["RedisBroker"]


class RedisBroker(IBroker):
    def __init__(self, redis_url: str):
        self._redis = redis.Redis.from_url(redis_url)

    def get_dedup_key(self, key: str) -> str | None:
        value = self._redis.get(key)
        if value:
            return value.decode("utf-8")
        return None

    def set_dedup_key(self, key: str, value: str, expire: int) -> None:
        self._redis.setex(key, expire, value)
