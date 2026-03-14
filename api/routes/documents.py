from fastapi import APIRouter, Depends, UploadFile, File
from services.document_processor import extract_text
from services.text_chunker import chunk_text
from services.embedding_service import embedding_service
from database.models import DocumentChunk
from sqlalchemy.orm import Session
import shutil
import uuid

from database.db import get_db
from database.models import Document

router = APIRouter()


@router.post("/documents")
def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):

    allowed_extensions = ["pdf", "txt", "docx"]

    file_extension = file.filename.split(".")[-1].lower()

    if file_extension not in allowed_extensions:
        return {"error": "File type not allowed"}

    unique_filename = f"{uuid.uuid4()}_{file.filename}"
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
