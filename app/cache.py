import os
import json
import redis
import logging

logger = logging.getLogger(__name__)

_redis = None


def get_redis():
    global _redis
    if _redis is None:
        try:
            _redis = redis.Redis(
                host=os.environ.get("REDIS_HOST", "localhost"),
                port=6379,
                db=0,
                decode_responses=True,
                socket_connect_timeout=2
            )
            _redis.ping()
            logger.info("Redis connected", extra={"component": "cache"})
        except redis.ConnectionError:
            logger.warning("Redis unavailable, caching disabled", extra={"component": "cache"})
            _redis = None
    return _redis


def cache_get(key):
    r = get_redis()
    if r is None:
        return None
    try:
        val = r.get(key)
        if val:
            logger.info("Cache HIT", extra={"component": "cache", "key": key})
            return json.loads(val)
        logger.info("Cache MISS", extra={"component": "cache", "key": key})
    except Exception:
        pass
    return None


def cache_set(key, data, ttl=30):
    r = get_redis()
    if r is None:
        return
    try:
        r.set(key, json.dumps(data, default=str), ex=ttl)
        logger.info("Cache SET", extra={"component": "cache", "key": key})
    except Exception as e:
        logger.warning("Cache SET failed", extra={"component": "cache", "error": str(e)})


def cache_invalidate(key):
    r = get_redis()
    if r is None:
        return
    try:
        r.delete(key)
    except Exception:
        pass