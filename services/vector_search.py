import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def find_similar_chunks(query_embedding, chunks, top_k=5):

    chunk_embeddings=[]
    chunk_texts=[]

    for chunk in chunks:
        if chunk.embedding is None:
            continue
        chunk_embeddings.append(chunk.embedding)
        chunk_texts.append(chunk.chunk_text)

    if len(chunk_embeddings) ==0:
        return []

    chunk_embeddings= np.array(chunk_embeddings)
    query_embedding = np.array(query_embedding).reshape(1,-1)

    

    similarities = cosine_similarity(query_embedding, chunk_embeddings)[0]

    top_indices = similarities.argsort()[-top_k:][::-1]

    results=[]

    for idx in top_indices:
        results.append({
            "chunk_text" : chunk_texts[idx],
            "score": float(similarities[idx])
            })
    return results
