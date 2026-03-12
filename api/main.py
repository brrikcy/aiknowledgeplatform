from fastapi import FastAPI
from database.db import engine, Base,get_db
from database import models
from database.models import Document
from sqlalchemy.orm import Session
from fastapi import Depends


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
def create_document(file_name: str,storage_path: str, db: Session = Depends(get_db)):
    document=Document(
            file_name=file_name,
            storage_path=storage_path
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

