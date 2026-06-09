import pickle
from rank_bm25 import BM25Okapi
from services.qdrant_service import qdrant, COLLECTION_NAME
from services.cache_service import get_bytes, set_bytes, BM25_CACHE_KEY
from services.logger_service import get_logger

logger = get_logger("bm25_service")


def build_bm25_index():
    all_points = qdrant.scroll(
        collection_name=COLLECTION_NAME,
        limit=10000,
        with_payload=True,
        with_vectors=False
    )[0]

    if not all_points:
        return None, []

    chunks = []
    for point in all_points:
        chunk_text = point.payload.get("chunk_text") or ""
        chunks.append({
            "id": str(point.id),
            "chunk_text": chunk_text,
            "document_id": point.payload.get("document_id"),
            "chunk_index": point.payload.get("chunk_index"),
            "tokens": chunk_text.lower().split()
        })

    tokenized_corpus = [c["tokens"] for c in chunks]
    bm25 = BM25Okapi(tokenized_corpus)

    return bm25, chunks


def bm25_search(query: str, top_k: int = 5) -> list[dict]:
    cached = get_bytes(BM25_CACHE_KEY)

    if cached:
        logger.info("BM25 cache hit")
        bm25, chunks = pickle.loads(cached)
    else:
        logger.info("BM25 cache miss — rebuilding index")
        bm25, chunks = build_bm25_index()

        if bm25 is None:
            return []

        set_bytes(BM25_CACHE_KEY, pickle.dumps((bm25, chunks)))
        logger.info("BM25 index cached")

    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)

    for i, chunk in enumerate(chunks):
        chunk["score"] = float(scores[i])

    results = sorted(chunks, key=lambda x: x["score"], reverse=True)
    results = [r for r in results if r["score"] > 0]

    return results[:top_k]


def invalidate_bm25_cache():
    from services.cache_service import delete
    delete(BM25_CACHE_KEY)
    logger.info("BM25 cache invalidated")
