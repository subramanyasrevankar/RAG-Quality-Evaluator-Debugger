    #          User asks a question
    #                   │
    #                   ▼
    #    make_cache_key(question, top_k)
    #                   │
    #                   ▼
    #         Search Redis using key
    #           │                 │
    #      Found in cache?      Not found
    #           │                 │
    #           ▼                 ▼
    #  Return cached answer   Generate new answer
    #           │                 │
    #           │                 ▼
    #           │        Store answer in Redis
    #           │                 │
    #           └──────────► Return answer


import json
import hashlib
import os
from upstash_redis import Redis
from dotenv import load_dotenv

load_dotenv()

redis_client = Redis(
    url=os.getenv("UPSTASH_REDIS_REST_URL"),
    token=os.getenv("UPSTASH_REDIS_REST_TOKEN")
)

CACHE_TTL = 3600


def make_cache_key(question: str, top_k: int) -> str:
    question_hash = hashlib.md5(question.lower().strip().encode()).hexdigest()
    return f"rag:query:{question_hash}:top_k:{top_k}"


def get_cached_result(question: str, top_k: int):
    try:
        key = make_cache_key(question, top_k)
        cached = redis_client.get(key)
        if cached:
            return json.loads(cached)
        return None
    except Exception as e:
        print(f"Cache get error: {e}")
        return None


def set_cached_result(question: str, top_k: int, result: dict) -> None:
    try:
        key = make_cache_key(question, top_k)
        redis_client.setex(key, CACHE_TTL, json.dumps(result))
    except Exception as e:
        print(f"Cache set error: {e}")


def delete_cached_result(question: str, top_k: int) -> None:
    try:
        key = make_cache_key(question, top_k)
        redis_client.delete(key)
    except Exception as e:
        print(f"Cache delete error: {e}")


def clear_all_cache() -> None:
    try:
        keys = redis_client.keys("rag:query:*")
        if keys:
            redis_client.delete(*keys)
    except Exception as e:
        print(f"Cache clear error: {e}")


def get_cache_stats() -> dict:
    try:
        keys = redis_client.keys("rag:query:*")
        return {
            "cached_queries": len(keys),
            "ttl_seconds": CACHE_TTL,
            "status": "connected"
        }
    except Exception as e:
        return {
            "cached_queries": 0,
            "ttl_seconds": CACHE_TTL,
            "status": f"error: {str(e)}"
        }