import os
import redis

REDIS_URL=os.getenv("REDIS_URL", "redis://localhost:6379")
client = redis.from_url(REDIS_URL, decode_responses=False)

BM25_CACHE_KEY = "bm25_index"
EMBEDDING_TTL = 3600

def get_bytes(key: str) -> bytes | None:
    try:
        return client.get(key)
    except Exception:
        return None

def set_bytes(key: str, value: bytes, ttl: int = None) -> None:
    try:
        if ttl:
            client.setex(key, ttl, value)
        else:
            client.set(key, value)
    except Exception:
        pass


def get_string(key: str) -> str | None:
    try:
        value = client.get(key)
        return value.decode("utf-8") if value else None
    except Exception:
        return None


def set_string(key: str, value: str, ttl: int = None) -> None:
    try:
        if ttl:
            client.setex(key, ttl, value.encode("utf-8"))
        else:
            client.set(key, value.encode("utf-8"))
    except Exception:
        pass

def delete(key: str) -> None:
    try:
        client.delete(key)
    except Exception:
        pass
