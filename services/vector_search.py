from services.qdrant_service import qdrant, COLLECTION_NAME


def find_similar_chunks(query_embedding,top_k=5):

    print("\n==== VECTOR SEARCH START ====")

    print("Query embedding length:", len(query_embedding))

    search_result = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=top_k
    )

    print("\nQdrant raw result:")
    print(search_result)

    results = []

    for hit in search_result.points:
        score = hit.score
        print("\n--- HIT ---")
        print("Score:", score)
        print("Payload:", hit.payload)

        chunk_text = hit.payload.get("chunk_text")

        if score < 0.2:
            continue

        if chunk_text:
            results.append({
                "chunk_text" : chunk_text,
                "score" : score
                })
    
    results = sorted(results, key=lambda x: x["score"], reverse=True)
    print("\nFiltered + sorted  chunks:", results)
    print("==== VECTOR SEARCH END ====\n")

    return results
