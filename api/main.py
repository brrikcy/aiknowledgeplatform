from fastapi import FastAPI

app=FastAPI(
        title="Knowledge AI Platform",
        version="0.1"
    )

@app.get("/")
def root():
    return {"status" : "running"}
