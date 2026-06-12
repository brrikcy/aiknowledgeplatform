from services.vector_search import find_similar_chunks
from services.bm25_service import bm25_search
from services.embedding_service import embedding_service

def hybrid_search(query, top_k=5, k=60):
    query_embedding = embedding_service.generate_embedding(query)
    vector_results = find_similar_chunks(query_embedding, top_k=top_k)
    bm25_results = bm25_search(query, top_k=top_k)

    rrf_scores = {}
    chunk_metadata = {}

    for rank, result in enumerate(vector_results):
        chunk_text = result["chunk_text"]
        rrf_scores[chunk_text] = rrf_scores.get(chunk_text, 0) + 1 / (k + rank + 1)
        chunk_metadata[chunk_text] = result.get("document_description", "")

    for rank, result in enumerate(bm25_results):
        chunk_text = result["chunk_text"]
        rrf_scores[chunk_text] = rrf_scores.get(chunk_text, 0) + 1 / (k + rank + 1)
        if chunk_text not in chunk_metadata:
            chunk_metadata[chunk_text] = result.get("document_description", "")

    fused_results = []
    for chunk_text, score in rrf_scores.items():
        fused_results.append({
            "chunk_text": chunk_text,
            "document_description": chunk_metadata.get(chunk_text, ""),
            "score": round(score, 6)
        })

    fused_results = sorted(fused_results, key=lambda x: x["score"], reverse=True)
    return fused_results[:top_k]
