from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import StreamingResponse
from services.document_processor import extract_text
from services.text_chunker import chunk_text
from services.embedding_service import embedding_service
from services.vector_search import find_similar_chunks
from services.rag_service import generate_answer
from services.qdrant_service import qdrant, COLLECTION_NAME
from services.hybrid_search import hybrid_search
from services.reranker_service import rerank
from services.agent_service import run_agent, run_agent_stream
from services.bm25_service import invalidate_bm25_cache
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
    invalidate_bm25_cache()
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

    results = hybrid_search(request.query)

    reranked_results = rerank(request.query, results)

    return {"query": request.query, "results": reranked_results}

@router.post("/ask")
def ask_question(request: QueryRequest, db: Session = Depends(get_db)):
    result= run_agent(request.query)
    return result

@router.post("/ask/stream")
def ask_question_stream(request: QueryRequest):
    def token_generator():
        for token in run_agent_stream(request.query):
            yield token

    return StreamingResponse(
            token_generator(),
            media_type="text/event-stream"
        )
