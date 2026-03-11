from fastapi import FastAPI
from database.db import engine

app=FastAPI(
        title="Knowledge AI Platform",
        version="0.1"
    )

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
