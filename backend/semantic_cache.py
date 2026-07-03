#              User asks a question
#                       │
#                       ▼
#        Convert question into embedding
#                       │
#                       ▼
#      Retrieve all stored embeddings from Redis
#                       │
#                       ▼
#     Compare new embedding with each stored one
#                       │
#           ┌───────────┴───────────┐
#           │                       │
#  Similarity ≥ 0.92?           No match found
#           │                       │
#           ▼                       ▼
#  Return cached result      Generate a new answer
#           │                       │
#           │             Create embedding + cache it
#           │                       │
#           └──────────────► Return answer

import json
import hashlib
import os
from upstash_redis import Redis
from sentence_transformers import SentenceTransformer, util
from dotenv import load_dotenv

load_dotenv()
redis_client = Redis(
    url=os.getenv("UPSTASH_REDIS_REST_URL"),
    token=os.getenv("UPSTASH_REDIS_REST_TOKEN")
)

model = SentenceTransformer('all-MiniLM-L6-v2') 
SEMANTIC_TTL = 3600
SIMILARITY_THRESHOLD = 0.92
EMBEDDING_PREFIX = "rag:embedding:"

def make_embedding_key(question: str) -> str:
    question_hash = hashlib.md5(question.lower().strip().encode()).hexdigest()
    return f"{EMBEDDING_PREFIX}{question_hash}"


def store_question_embedding(question: str, result: dict) -> None:
    try:
        embedding = model.encode(question).tolist()
        payload = {
            "question": question,
            "embedding": embedding,
            "result": result
        }
        key = make_embedding_key(question)
        redis_client.setex(key, SEMANTIC_TTL, json.dumps(payload))
    except Exception as e:
        print(f"Semantic cache store error: {e}")



def find_similar_cached_result(question: str):
    """
    Checks if a semantically similar question was asked before.
    Steps:
    1. Get all stored embeddings from Redis
    2. Compare new question embedding with each stored one
    3. If similarity above threshold — return cached result

    This handles near-duplicate questions like:
    'What is ML?' vs 'Can you explain machine learning?'
    """
    try:
        keys = redis_client.keys(f"{EMBEDDING_PREFIX}*")
        if not keys:
            return None

        new_embedding = model.encode(question, convert_to_tensor=True)

        for key in keys:
            cached = redis_client.get(key)
            if not cached:
                continue

            data = json.loads(cached)
            stored_embedding = data.get("embedding")
            if not stored_embedding:
                continue

            import torch
            stored_tensor = torch.tensor(stored_embedding)
            similarity = util.cos_sim(new_embedding, stored_tensor).item()

            if similarity >= SIMILARITY_THRESHOLD:
                print(f"Semantic cache HIT — similarity: {round(similarity, 3)}")
                result = data["result"]
                result["cache_hit"] = True
                result["similarity_score"] = round(similarity, 3)
                result["matched_question"] = data["question"]
                return result

        return None

    except Exception as e:
        print(f"Semantic cache search error: {e}")
        return None
    
def clear_semantic_cache() -> None:
    try:
        keys = redis_client.keys(f"{EMBEDDING_PREFIX}*")
        if keys:
            redis_client.delete(*keys)
    except Exception as e:
        print(f"Semantic cache clear error: {e}")


def get_semantic_cache_stats() -> dict:
    try:
        keys = redis_client.keys(f"{EMBEDDING_PREFIX}*")
        return {
            "semantic_cached_queries": len(keys),
            "similarity_threshold": SIMILARITY_THRESHOLD,
            "status": "connected"
        }
    except Exception as e:
        return {
            "semantic_cached_queries": 0,
            "similarity_threshold": SIMILARITY_THRESHOLD,
            "status": f"error: {str(e)}"
        }