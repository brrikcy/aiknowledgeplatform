import json
import hashlib
from sentence_transformers import SentenceTransformer
from services.cache_service import get_bytes, set_bytes, EMBEDDING_TTL
from services.logger_service import get_logger

logger = get_logger("embedding_service")


class EmbeddingService:

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def _cache_key(self, text: str) -> str:
        hash_ = hashlib.md5(text.encode("utf-8")).hexdigest()
        return f"embedding:{hash_}"

    def generate_embedding(self, text: str) -> list[float]:
        key = self._cache_key(text)
        cached = get_bytes(key)

        if cached:
            logger.info("embedding cache hit")
            return json.loads(cached.decode("utf-8"))

        logger.info("embedding cache miss — generating")
        embedding = self.model.encode(text).tolist()
        set_bytes(key, json.dumps(embedding).encode("utf-8"), ttl=EMBEDDING_TTL)

        return embedding


embedding_service = EmbeddingService()
