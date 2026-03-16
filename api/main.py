from fastapi import FastAPI
from database.db import engine, Base
from database import models
from services.qdrant_service import create_collection

from api.routes import documents

app = FastAPI(
    title="Knowledge AI Platform",
    version="0.1"
)

Base.metadata.create_all(bind=engine)

create_collection()

app.include_router(documents.router)


@app.get("/")
def root():
    return {"status": "running"}


@app.get("/db-test")
def test_db():
    try:
        connection = engine.connect()
        connection.close()
        return {"database": "connected"}
    except Exception as e:
        return {"database": "error", "details": str(e)}
