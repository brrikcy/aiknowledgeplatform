from services.qdrant_service import qdrant, COLLECTION_NAME
from database.models import DocumentChunk
import uuid


def find_similar_chunks(query_embedding, db, top_k=5):

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

        print("\n--- HIT ---")
        print("Hit ID:", hit.id)
        print("Score:", hit.score)
        print("Payload:", hit.payload)

        payload = hit.payload

        try:
            document_id = uuid.UUID(payload["document_id"])
        except Exception as e:
            print("UUID conversion failed:", e)
            continue

        chunk_index = payload["chunk_index"]

        print("Converted document_id:", document_id)
        print("Chunk index:", chunk_index)

        chunk = db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id,
            DocumentChunk.chunk_index == chunk_index
        ).first()

        print("DB query result:", chunk)

        if chunk:
            results.append({
                "chunk_text": chunk.chunk_text,
                "chunk_index": chunk.chunk_index
            })

    print("\nFinal retrieved chunks:", results)
    print("==== VECTOR SEARCH END ====\n")

    return results
