from sentence_transformers import CrossEncoder

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

reranker = CrossEncoder(MODEL_NAME)
def rerank(query : str, chunks : list[dict], top_n : int =3) -> list[dict]:
    if not chunks:
        return []

    pairs  = [[query, chunk ["chunk_text"]] for chunk in chunks]
    scores = reranker.predict(pairs)

    for i, chunk in enumerate(chunks):
        chunk["rerank_score"]=float(scores[i])

    reranked = sorted(chunks,key=lambda x: x["rerank_score"], reverse=True)

    return reranked[:top_n]

