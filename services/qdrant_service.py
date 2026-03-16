from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance,VectorParams

qdrant = QdrantClient(host="localhost", port=6333)

COLLECTION_NAME = "document_embeddings"

def create_collection():

    collections = qdrant.get_collections().collections
    collection_names = [c.name for c in collections]

    if COLLECTION_NAME not in collection_names:

        qdrant.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=384,
                    distance=Distance.COSINE
                    ),
                )
