from fastapi import APIRouter, Depends, UploadFile, File
from services.document_processor import extract_text
from services.text_chunker import chunk_text
from services.embedding_service import embedding_service
from services.vector_search import find_similar_chunks
from services.rag_service import generate_answer
from services.qdrant_service import qdrant, COLLECTION_NAME
from qdrant_client.http.models import PointStruct

from sqlalchemy.orm import Session
import shutil
import os
import uuid
from pydantic import BaseModel
from database.db import get_db
from database.models import Document,DocumentChunk

router = APIRouter()


class QueryRequest(BaseModel):
    query : str


@router.post("/documents")
def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):

    allowed_extensions = ["pdf", "txt", "docx"]

    file_extension = file.filename.split(".")[-1].lower()

    if file_extension not in allowed_extensions:
        return {"error": "File type not allowed"}

    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    os.makedirs("storage/documents", exist_ok=True)
    file_location = f"storage/documents/{unique_filename}"

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = extract_text(file_location)
    chunks=chunk_text(text)


    document = Document(
        file_name=file.filename,
        storage_path=file_location,
        text_content=text
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    for index, chunk in enumerate(chunks):

        embedding=embedding_service.generate_embedding(chunk)

        document_chunk = DocumentChunk(
                document_id=document.id,
                chunk_text=chunk,
                chunk_index=index,
                embedding=embedding
                )
        db.add(document_chunk)
        db.flush()

        vector_id = f"{document.id}_{index}"
        qdrant.upsert(
                collection_name = COLLECTION_NAME,
                points=[
                    PointStruct(
                        id=str(document_chunk.id),
                        vector=embedding,
                        payload={
                            "document_id" : str(document.id),
                            "chunk_index" : index,
                            "chunk_text" : chunk
                            }
                        )
                    ]
                )


    db.commit()
    return {
        "id": str(document.id),
        "file_name": document.file_name,
        "status": document.status
    }


@router.get("/documents")
def get_documents(db: Session = Depends(get_db)):

    documents = db.query(Document).all()

    result = []

    for doc in documents:
        result.append({
            "id": str(doc.id),
            "file_name": doc.file_name,
            "status": doc.status
        })

    return result


@router.get("/documents/{document_id}")
def get_document(document_id: str, db: Session = Depends(get_db)):

    document = db.query(Document).filter(Document.id == document_id).first()

    if document is None:
        return {"error": "Document not found"}

    return {
        "id": str(document.id),
        "file_name": document.file_name,
        "storage_path": document.storage_path,
        "status": document.status
    }


@router.delete("/documents/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db)):

    document = db.query(Document).filter(Document.id == document_id).first()

    if document is None:
        return {"error": "Document not found"}

    db.delete(document)
    db.commit()

    return {"message": "Document deleted successfully"}


@router.post("/search")
def search_documents(request: QueryRequest, db: Session = Depends(get_db)):
    query_embedding = embedding_service.generate_embedding(request.query)

    results = find_similar_chunks(query_embedding)

    return results

@router.post("/ask")
def ask_question(request: QueryRequest, db: Session = Depends(get_db)):

    query_embedding = embedding_service.generate_embedding(request.query)
    search_results = find_similar_chunks(query_embedding)
    context_chunks=[r["chunk_text"] for r in search_results[:3]]
    answer=generate_answer(request.query,context_chunks)

    if not context_chunks:
        return {
                "question" : request.query,
                "answer" : "No relevant documents found",
                "context" : []
                }

    return { 
    "question" : request.query,
    "answer" : answer,
    "context" : context_chunks
    }
