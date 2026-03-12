from fastapi import FastAPI, UploadFile, File
from database.db import engine, Base,get_db
from database import models
from database.models import Document
from sqlalchemy.orm import Session
from fastapi import Depends
import shutil
import os
import uuid


app=FastAPI(
        title="Knowledge AI Platform",
        version="0.1"
    )
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status" : "running"}

@app.get("/db-test")
def test_db():
    try:
        connection=engine.connect()
        connection.close()
        return {"database": "connected"}
    except Exception as e:
        return {"database": "error", "details":str(e)}

@app.post("/documents")
def upload_document(file: UploadFile = File(...),db: Session = Depends(get_db)):

    allowed_extensions= ["pdf", "txt", "docx"]
    file_extension = file.filename.split(".")[-1].lower()

    if file_extension not in allowed_extensions:
        return {"error": "File type not allowed"}

    unique_filename= f"{uuid.uuid4()}_{file.filename}"
    file_location=f"storage/documents/{unique_filename}"

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    document=Document(
            file_name=file.filename,
            storage_path=file_location
            )
    db.add(document)
    db.commit()
    db.refresh(document)

    return {
            "id": str(document.id),
            "file_name":document.file_name,
            "status":document.status
        }
@app.get("/documents")
def get_documents(db: Session = Depends(get_db)):
    documents=db.query(Document).all()
    result=[]

    for doc in documents:
        result.append({
            "id": str(doc.id),
            "file_name": doc.file_name,
            "status" : doc.status
            })
    return result

@app.get("/documents/{document_id}")
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

@app.delete("/documents/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db)):

    document = db.query(Document).filter(Document.id == document_id).first()

    if document is None:
        return {"error" : "Document not found"}

    db.delete(document)
    db.commit()

    return {"message" : "Document deleted successfully"}

