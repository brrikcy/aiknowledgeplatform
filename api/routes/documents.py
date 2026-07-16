from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks
from typing import Optional
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
from qdrant_client.http.models import PointStruct,PointIdsList
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


def process_document(document_id: str, file_location: str, filename: str, description: Optional[str]):
    from database.db import SessionLocal
    db = SessionLocal()
    try:
        text = extract_text(file_location)
        chunks = chunk_text(text)

        # Generate description
        if not description:
            from services.rag_service import generate_document_description
            description = generate_document_description(filename, text)

        # Update document record with description and text
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return
        document.text_content = text
        document.document_description = description
        document.status = "processing"
        db.commit()

        # Generate embeddings and store chunks
        for index, chunk in enumerate(chunks):
            embedding = embedding_service.generate_embedding(chunk)

            document_chunk = DocumentChunk(
                document_id=document.id,
                chunk_text=chunk,
                chunk_index=index,
                embedding=embedding
            )
            db.add(document_chunk)
            db.flush()

            qdrant.upsert(
                collection_name=COLLECTION_NAME,
                points=[
                    PointStruct(
                        id=str(document_chunk.id),
                        vector=embedding,
                        payload={
                            "document_id": str(document.id),
                            "chunk_index": index,
                            "chunk_text": chunk,
                            "document_description": description
                        }
                    )
                ]
            )

        db.commit()
        invalidate_bm25_cache()

        # Mark as ready
        document.status = "ready"
        db.commit()

    except Exception as e:
        from services.logger_service import get_logger
        logger = get_logger("document_processor")
        logger.error("background processing failed", extra={"extra": {
            "document_id": document_id,
            "error": str(e)
        }})
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.status = "failed"
            db.commit()
    finally:
        db.close()



@router.post("/documents")
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    allowed_extensions = ["pdf", "txt", "docx"]
    file_extension = file.filename.split(".")[-1].lower()

    if file_extension not in allowed_extensions:
        return {"error": "File type not allowed"}

    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    os.makedirs("storage/documents", exist_ok=True)
    file_location = f"storage/documents/{unique_filename}"

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    document = Document(
        file_name=file.filename,
        storage_path=file_location,
        status="processing"
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    background_tasks.add_task(
        process_document,
        str(document.id),
        file_location,
        file.filename,
        description
    )

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

    chunks = db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document.id
            ).all()

    if chunks:
        chunk_ids = [str(chunk.id) for chunk in chunks]
        qdrant.delete(
                collection_name=COLLECTION_NAME,
                points_selector=PointIdsList(points=chunk_ids)
                )

    if os.path.exists(document.storage_path):
        os.remove(document.storage_path)

    db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document.id
            ).delete()



    db.delete(document)
    db.commit()
    invalidate_bm25_cache()

    return {"message": "Document deleted successfully"}


@router.post("/search")
def search_documents(request: QueryRequest):

    results = hybrid_search(request.query)

    reranked_results = rerank(request.query, results)

    return {"query": request.query, "results": reranked_results}

@router.post("/ask")
def ask_question(request: QueryRequest):
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
