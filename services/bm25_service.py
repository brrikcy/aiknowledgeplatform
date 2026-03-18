from rank_bm25 import BM25Okapi
from services.qdrant_service import qdrant, COLLECTION_NAME

def bm25_search(query, top_k=5):

    all_points = qdrant.scroll(
            collection_name=COLLECTION_NAME,
            limit=10000,
            with_payload=True,
            with_vectors=False
            )[0]

    if not all_points:
        return []

    chunks=[]

    for point in all_points:
        chunk_text = point.payload.get("chunk_text") or ""
        chunks.append({
            "id": point.id,
            "chunk_text": chunk_text,
            "document_id": point.payload.get("document_id"),
            "chunk_index": point.payload.get("chunk_index"),
            "tokens": chunk_text.lower().split()
            })
    
    tokenized_corpus=[c["tokens"] for c in chunks]

    bm25= BM25Okapi(tokenized_corpus)

    tokenized_query = query.lower().split()

    scores=bm25.get_scores(tokenized_query)

    for i, chunk in enumerate(chunks):
        chunk["score"] = float(scores[i])

    ranked=sorted(chunks, key=lambda x:x["score"], reverse=True)

    results=[]

    for chunk in ranked[:top_k]:
        if chunk["score"] > 0:
            results.append({
                "chunk_text" : chunk["chunk_text"],
                "score" : chunk["score"]
                })
    return results
