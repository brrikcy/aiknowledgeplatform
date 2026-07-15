# Knowledge AI Platform

A **self-hosted AI knowledge platform** that allows organizations to upload internal documents and interact with them using **LLM-powered semantic search and Retrieval Augmented Generation (RAG)**.

The platform runs **entirely inside the organization's infrastructure**, ensuring that sensitive company data never leaves their environment.

---

# Project Goal

The goal of this project is to build a **production-style AI infrastructure platform** capable of:

* Ingesting enterprise documents with automatic context generation
* Extracting and processing document text with sentence-aware chunking
* Generating semantic embeddings
* Enabling semantic search over internal knowledge
* Supporting Retrieval Augmented Generation (RAG)
* Hybrid retrieval combining vector search and keyword search
* Reranking retrieved chunks using a cross-encoder
* Fast query routing with configurable intent classification
* Streaming LLM responses token by token
* Structured JSON logging with per-request tracing
* Redis caching for BM25 index and query embeddings
* Python SDK for programmatic access
* Full document lifecycle management
* Running fully locally using containerized infrastructure

---

# Core Features

* Upload enterprise documents (PDF, DOCX, TXT)
* Automatic document parsing
* Async document processing — upload returns instantly
* Auto-generated document descriptions using LLM
* Document context injection — every chunk labeled with source
* Sentence-aware chunking — never splits mid-sentence or mid-word
* Embedding generation using transformer models
* Vector similarity search
* BM25 keyword search
* Hybrid search with Reciprocal Rank Fusion (RRF)
* Cross-encoder reranking of retrieved chunks
* Configurable intent classification (embedding-based, toggleable)
* LLM-powered question answering
* Streaming responses via Server-Sent Events (SSE)
* Structured JSON logging with request ID tracing
* Per-stage pipeline timing
* Redis caching for BM25 index and embeddings
* Python SDK for programmatic integration
* Full document deletion — cleans all data stores
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
  |-- Document Upload (async)
  |        |
  |        v
  |    Save file → DB record (status=processing) → Return instantly
  |        |
  |        v [Background Task]
  |    Extract text (layout-aware PyMuPDF extraction)
  |    Split into sentences → group into chunks (never mid-sentence)
  |    Generate description (LLM) → Generate embeddings
  |    Store in Qdrant + PostgreSQL → Invalidate BM25 cache
  |    status=ready
  |
  v
User Query
  |
  v
[Optional] Intent Classification (default OFF)
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
              |
              v
   Cross-Encoder Reranking
              |
              v
   Build Context with Source Labels
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
* PyMuPDF (layout-aware text extraction)
* python-docx

### Chunking

* Regex-based sentence splitting (no external NLP dependency)
* Sentences grouped up to ~500 chars per chunk
* 1-sentence overlap carried between chunks
* Never splits mid-sentence or mid-word

### Retrieval

* rank_bm25 (BM25Okapi)
* Reciprocal Rank Fusion
* Cross-Encoder Reranking
* Document context injection per chunk

### Intent Classification

* Embedding-based classifier (all-MiniLM-L6-v2 cosine similarity)
* Toggleable via INTENT_CLASSIFIER_ENABLED env var
* Default: OFF (all queries routed to knowledge base)
* Planned: retrieval-confidence routing (Day 28)

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

## Days 1-24 — Complete

Full stack running. PostgreSQL, Qdrant, Redis, FastAPI containerized. Python SDK. Redis caching. DELETE endpoint fully cleans all stores. Async document upload with LLM-generated descriptions. Document context injection per chunk. Intent classification overhauled — embedding-based, toggleable, default OFF.

---

## Day 25 — Sentence-Aware Chunking

Replaced character-level chunking with sentence-aware chunking, directly fixing the majority of retrieval quality issues identified during testing.

Key implementations:

- Rewrote `text_chunker.py` — regex-based sentence splitting, no new dependency
- Sentences grouped into chunks up to ~500 chars, never split mid-sentence
- 1-sentence overlap carried forward between chunks for context continuity
- Improved `document_processor.py` PDF extraction to use PyMuPDF's layout-aware `get_text("text")` mode
- Replaced remaining `print()` warning with structured logger call
- Full data wipe and re-ingestion performed (Qdrant, PostgreSQL, Redis, storage)

Sentence splitting logic:

```python
sentence_endings = re.compile(r'(?<=[.!?])\s+(?=[A-Z])|(?<=[.!?])\n+')
```

Chunking logic:

```
Split text into sentences
      ↓
Group sentences until adding one would exceed chunk_size (~500 chars)
      ↓
Start new chunk, carrying forward last N sentences as overlap
      ↓
Never break a sentence in the middle
```

Verified fixes — previously failing queries now answered correctly and completely:

- "what are ajmals educational qualifications?" — full, accurate answer (previously failed on `elopment (RGNIYD)` fragment)
- "what core AI/ML skills does the person have?" — complete skill list returned (previously cut off at `TensorF`)

Known non-blocking issue: occasional missing space between text runs in PDF extraction (e.g. `M.Sc.Computer`) — a PyMuPDF text-run boundary artifact, not a chunking issue. Does not affect answer correctness.

Operational note: uploading via Swagger UI (`/docs`) requires clearing the default `"string"` placeholder in the optional `description` field before submitting, or it will override auto-generation with the literal text `"string"`. Uploading via curl without the field works correctly.

---

# API Reference

## Document Management

```
POST   /documents              Upload a document (async, returns instantly)
GET    /documents              List all documents
GET    /documents/{id}         Get document by ID (poll for status: ready)
DELETE /documents/{id}         Delete document and all associated data
```

## Search and QA

```
POST   /search                 Hybrid search with reranking
POST   /ask                    Question answering
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
INTENT_CLASSIFIER_ENABLED=false
```

---

## Start the full stack

```
docker compose up --build
```

For subsequent starts:

```
docker compose up
```

---

## Upload a document

```bash
curl -X POST http://localhost:8000/documents \
  -F "file=@document.pdf"
```

Note: if using Swagger UI (`/docs`), clear the default `"string"` value in the `description` field before executing, or leave it blank.

---

## Open API docs

```
http://localhost:8000/docs
```

---

# Optimization Roadmap

- Day 22: Fix DELETE endpoint ✅
- Day 23: Document context injection + async upload ✅
- Day 24: Intent classification overhaul ✅
- Day 25: Sentence-aware chunking ✅
- Day 26: Document deduplication
- Day 27: Pre-built llama-cpp-python wheel
- Day 28: Retrieval-confidence routing (post-rerank threshold, calibrated on clean chunks)

---

# Future Improvements

* Celery-based async task queue
* Fix PDF text-run spacing artifact (minor)
* Web dashboard
* Observability dashboard (Grafana + Loki)
* Kubernetes deployment
* Multi-tenant architecture
* SDK pip-installable package
* Adaptive top-k retrieval
* Query rewriting / expansion

---

# Author

Ajmal
AI Engineer | MSc Artificial Intelligence & Machine Learning
