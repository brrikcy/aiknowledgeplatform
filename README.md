# Knowledge AI Platform

A **self-hosted AI knowledge platform** that allows organizations to upload internal documents and interact with them using **LLM-powered semantic search and Retrieval Augmented Generation (RAG)**.

The platform runs **entirely inside the organization's infrastructure**, ensuring that sensitive company data never leaves their environment.

---

# Project Goal

The goal of this project is to build a **production-style AI infrastructure platform** capable of:

* Ingesting enterprise documents with automatic context generation
* Extracting and processing document text
* Chunking documents for semantic retrieval
* Generating semantic embeddings
* Enabling semantic search over internal knowledge
* Supporting Retrieval Augmented Generation (RAG)
* Hybrid retrieval combining vector search and keyword search
* Reranking retrieved chunks using a cross-encoder
* Routing user queries via an intent-classification agent
* Streaming LLM responses token by token
* Structured JSON logging with per-request tracing
* Redis caching for BM25 index and query embeddings
* Python SDK for programmatic access
* Full document lifecycle management (upload, search, delete)
* Running fully locally using containerized infrastructure

---

# Core Features

* Upload enterprise documents (PDF, DOCX, TXT)
* Automatic document parsing
* Async document processing — upload returns instantly, processing in background
* Auto-generated document descriptions using LLM (filename + content)
* Optional manual description override at upload time
* Document context injection — every chunk labeled with its source description
* Text chunking for retrieval
* Embedding generation using transformer models
* Vector similarity search
* BM25 keyword search
* Hybrid search with Reciprocal Rank Fusion (RRF)
* Cross-encoder reranking of retrieved chunks
* Intent-classification agent for query routing
* LLM-powered question answering
* Streaming responses via Server-Sent Events (SSE)
* Structured JSON logging with request ID tracing
* Per-stage pipeline timing (intent, search, rerank, LLM)
* Redis caching for BM25 index and embeddings
* Python SDK for programmatic integration
* Full document deletion — cleans Qdrant, PostgreSQL, disk, and cache
* Full Docker Compose stack (PostgreSQL + Qdrant + Redis + Backend)
* Fully local AI inference
* Containerized infrastructure

---

# System Architecture

```
Users / Python SDK
  |
  v
FastAPI Backend (Docker)
  |
  |-- Document Upload
  |        |
  |        v
  |    Save file to disk
  |    Create DB record (status=processing)
  |    Return instantly ← user gets response here
  |        |
  |        v
  |    [Background Task]
  |    Extract text
  |    Generate description (LLM: filename + content)
  |    Generate embeddings per chunk
  |    Store in PostgreSQL + Qdrant (with description in payload)
  |    Invalidate BM25 cache
  |    Update status=ready
  |
  |-- Document Delete
  |        |
  |        v
  |    Delete Qdrant vectors
  |    Delete file from disk
  |    Delete PostgreSQL chunks + document
  |    Invalidate BM25 cache
  |
  v
User Query
  |
  v
Intent Classification (LLM)
  |
  |-- out_of_scope → Fixed Response
  |
  \-- knowledge_base_query
        |
        v
Query Embedding (Redis cache → generate if miss)
        |
        v
┌──────────────────────────────────────┐
│  Vector Search (Qdrant ANN)          │
│  BM25 Search (Redis cache → rebuild) │
└─────────────┬────────────────────────┘
              |
              v
  Reciprocal Rank Fusion (RRF)
  (carries document_description per chunk)
              |
              v
   Cross-Encoder Reranking
              |
              v
   Build Context with Source Labels:
   "Chunk 1 [Source: Resume of Ajmal P]:
    M.Sc. Computer Science..."
              |
              v
     Generate Answer (LLM)
              |
              v
     Response / Stream to Client
```

---

# Technology Stack

### Backend

* Python
* FastAPI
* Pydantic

### Database

* PostgreSQL
* SQLAlchemy

### Vector Database

* Qdrant

### Cache

* Redis 7
* BM25 index cached as serialized pickle
* Query embeddings cached as JSON with 1hr TTL

### AI / NLP

* Sentence Transformers (all-MiniLM-L6-v2)
* Cross-Encoder (ms-marco-MiniLM-L-6-v2)
* llama-cpp-python (Phi-3-mini-4k-instruct-Q4_K_M)
* PyMuPDF
* python-docx

### Retrieval

* rank_bm25 (BM25Okapi)
* Reciprocal Rank Fusion
* Cross-Encoder Reranking
* Document context injection per chunk

### Agent

* Intent classification via Phi-3-mini
* Tool-routing agent (knowledge_base_query / out_of_scope)

### Streaming

* Server-Sent Events (SSE)
* FastAPI StreamingResponse

### Observability

* Structured JSON logging
* Per-request UUID tracing
* Per-stage pipeline timing

### SDK

* Python client (requests + httpx)
* Wraps all API endpoints
* Optional description parameter on upload
* Streaming support via httpx

### Infrastructure

* Docker
* Docker Compose
* WSL (development environment)

---

# Project Structure

```
knowledge-ai-platform
|
|-- api
|   |-- main.py
|   \-- routes
|        \-- documents.py
|
|-- database
|   |-- db.py
|   \-- models.py
|
|-- services
|   |-- document_processor.py
|   |-- text_chunker.py
|   |-- embedding_service.py
|   |-- vector_search.py
|   |-- bm25_service.py
|   |-- hybrid_search.py
|   |-- reranker_service.py
|   |-- rag_service.py
|   |-- agent_service.py
|   |-- logger_service.py
|   |-- cache_service.py
|   \-- qdrant_service.py
|
|-- sdk
|   |-- __init__.py
|   |-- client.py
|   |-- exceptions.py
|   \-- example.py
|
|-- storage
|   \-- documents
|
|-- models
|   \-- Phi-3-mini-4k-instruct-Q4_K_M.gguf  (not tracked in git)
|
|-- Dockerfile
|-- docker-compose.yml
|-- .env                                      (not tracked in git)
|-- .dockerignore
|-- requirements.txt
\-- README.md
```

---

# Current Project Status

## Days 1-22 — Complete

Full stack running. PostgreSQL, Qdrant, Redis, FastAPI containerized. Python SDK implemented. Redis caching verified. DELETE endpoint fully cleans all data stores.

---

## Day 23 — Document Context Injection + Async Upload

Solved the document identity problem — chunks now carry their source document description so the LLM knows which document each chunk came from.

Key implementations:

- Added `document_description` column to PostgreSQL `documents` table
- Added `generate_document_description(filename, text)` to `rag_service.py` — uses Phi-3-mini to generate a one-sentence description from filename + first 500 chars of content
- Upload endpoint restructured to async background processing:
  - HTTP response returns instantly with `status: "processing"`
  - Background task handles text extraction, description generation, embedding, Qdrant storage
  - Status transitions to `"ready"` on completion, `"failed"` on error
- `document_description` stored in Qdrant payload alongside `chunk_text`
- Context builder updated — each chunk prefixed with source label:
  ```
  Chunk 1 [Source: Resume of Muhammed Ajmal P, AI Developer]:
  M.Sc. Computer Science (Artificial Intelligence and Machine Learning)...
  ```
- `generate_answer()` and `generate_answer_stream()` updated to handle dict chunks
- `agent_service.py` updated to pass full chunk dicts instead of text strings
- `hybrid_search.py`, `vector_search.py`, `bm25_service.py` updated to carry `document_description` through pipeline
- SDK `upload()` accepts optional `description` parameter

Document status lifecycle:

```
Upload request received
      ↓
File saved, DB record created (status=processing)
      ↓
HTTP 200 returned instantly
      ↓
[Background]
Text extracted → Description generated → Chunks embedded → Qdrant stored
      ↓
status=ready
```

Verified fixes:

- "what are ajmals educational qualifications?" — now answered correctly
- "gimme the contact details of ajmal" — now returns phone and email correctly
- Document description visible in search results

Note: Documents uploaded before Day 23 have empty descriptions. Re-upload or wait for Day 25 (chunking overhaul) when all documents will be re-ingested.

---

# API Reference

## Document Management

```
POST   /documents              Upload a document (returns instantly, processes in background)
                               Optional form field: description (string)
GET    /documents              List all documents
GET    /documents/{id}         Get document by ID (poll for status: processing → ready)
DELETE /documents/{id}         Delete document and all associated data
```

## Search and QA

```
POST   /search                 Hybrid search with reranking
POST   /ask                    Agent-routed question answering
POST   /ask/stream             Streaming question answering (SSE)
```

## System

```
GET    /                       Health check
GET    /db-test                Database connectivity check
```

---

# Local Setup Instructions

## Prerequisites

* Docker and Docker Compose installed
* At least 8GB RAM
* At least 10GB free disk space

---

## Download LLM

```
mkdir -p models
cd models
wget https://huggingface.co/bartowski/Phi-3-mini-4k-instruct-GGUF/resolve/main/Phi-3-mini-4k-instruct-Q4_K_M.gguf
cd ..
```

Note: The embedding model (all-MiniLM-L6-v2) and reranking model (ms-marco-MiniLM-L-6-v2) are downloaded automatically on first run.

---

## Configure environment

Create a `.env` file in the project root:

```
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin123
POSTGRES_DB=knowledge_ai
DATABASE_URL=postgresql://admin:admin123@postgres:5432/knowledge_ai
QDRANT_HOST=qdrant
REDIS_URL=redis://redis:6379
MODEL_PATH=models/Phi-3-mini-4k-instruct-Q4_K_M.gguf
```

---

## Start the full stack

```
docker compose up --build
```

For subsequent starts (no code changes):

```
docker compose up
```

---

## Upload a document

```bash
# Auto-generate description from filename + content
curl -X POST http://localhost:8000/documents \
  -F "file=@document.pdf"

# Provide explicit description
curl -X POST http://localhost:8000/documents \
  -F "file=@document.pdf" \
  -F "description=Resume of Muhammed Ajmal P, AI Developer"
```

Poll for completion:

```bash
curl http://localhost:8000/documents/{id}
# Wait for status: "ready"
```

---

## Open API docs

```
http://localhost:8000/docs
```

---

## Use the Python SDK

```python
from sdk import KnowledgeClient

client = KnowledgeClient("http://localhost:8000")

# Upload with auto-generated description
client.upload("document.pdf")

# Upload with explicit description
client.upload("document.pdf", description="Resume of Muhammed Ajmal P")

# Ask a question
response = client.ask("what are ajmals educational qualifications?")
print(response["answer"])
```

---

# Optimization Roadmap

- Day 22: Fix DELETE endpoint ✅
- Day 23: Document context injection + async upload ✅
- Day 24: Shorten intent classification prompt
- Day 25: Sentence-aware chunking + diversity filtering
- Day 26: Document deduplication
- Day 27: Pre-built llama-cpp-python wheel (fast Docker builds)
- Day 28: Adaptive top-k retrieval

---

# Future Improvements

* Celery-based async task queue (upgrade from FastAPI BackgroundTasks)
* Multi-tool agent with full ReAct loop (requires stronger LLM)
* Web dashboard
* Observability dashboard (Grafana + Loki)
* Kubernetes deployment
* Multi-tenant architecture
* SDK pip-installable package

---

# Author

Ajmal
AI Engineer | MSc Artificial Intelligence & Machine Learning
