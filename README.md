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
* Text chunking for retrieval
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
  |    Extract text → Generate description (LLM)
  |    Generate embeddings → Store in Qdrant + PostgreSQL
  |    Invalidate BM25 cache → status=ready
  |
  v
User Query
  |
  v
[Optional] Intent Classification
  INTENT_CLASSIFIER_ENABLED=true:
    Embedding similarity → knowledge_base_query / out_of_scope
  INTENT_CLASSIFIER_ENABLED=false (default):
    All queries → knowledge_base_query
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
* PyMuPDF
* python-docx

### Retrieval

* rank_bm25 (BM25Okapi)
* Reciprocal Rank Fusion
* Cross-Encoder Reranking
* Document context injection per chunk

### Intent Classification

* Embedding-based classifier (all-MiniLM-L6-v2 cosine similarity)
* Toggleable via INTENT_CLASSIFIER_ENABLED env var
* Default: OFF (all queries routed to knowledge base)
* Planned: retrieval-confidence routing (Day 28, post chunking fix)

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

## Days 1-23 — Complete

Full stack running. PostgreSQL, Qdrant, Redis, FastAPI containerized. Python SDK. Redis caching. DELETE endpoint fully cleans all stores. Async document upload with LLM-generated descriptions. Document context injection per chunk.

---

## Day 24 — Intent Classification Overhaul

Replaced LLM-based intent classification with a fast embedding-based classifier. Added toggle for classifier on/off. Researched and deferred retrieval-confidence routing to Day 28.

Key changes:

- Removed Phi-3-mini from intent classification path entirely
- Implemented embedding-based classifier using cosine similarity between query and label embeddings
- Classification now takes 2-686ms vs 4,000-18,000ms previously (6000x improvement)
- Added `INTENT_CLASSIFIER_ENABLED` environment variable toggle
- Default set to `false` — all queries route to knowledge base, no false OOS
- Researched three alternative approaches:
  - BM25 token overlap routing — fast but lexical overlap ≠ relevance
  - NER + BM25 entity-anchored routing — valid but adds spacy dependency
  - Retrieval-confidence routing (post-rerank threshold) — most principled approach

Test results with classifier ON (embedding-based):

```
"what are ajmals technical skills?"  → KB  ✅
"what certifications does ajmal?"    → KB  ✅
"gimme ajmals phone number"          → KB  ✅
"what companies has ajmal worked?"   → KB  ✅
"hello how are you?"                 → OOS ✅
"what is the capital of france?"     → OOS ✅
"who invented the telephone?"        → OOS ✅
"thank you"                          → OOS ✅
"where did ajmal study?"             → OOS ❌ (should be KB)
"what is machine learning?"          → KB  ❌ (should be OOS)
```

Decision: classifier defaulted OFF pending Day 28 calibration after chunking improvements.

Planned Day 28: retrieval-confidence routing using cross-encoder reranker score threshold. Your data shows clear bimodal distribution:

```
Relevant chunks:   rerank_score > -8.0
Irrelevant chunks: rerank_score < -9.0
```

Threshold will be calibrated after Day 25 (sentence-aware chunking) stabilizes score distributions.

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

## Open API docs

```
http://localhost:8000/docs
```

---

# Optimization Roadmap

- Day 22: Fix DELETE endpoint ✅
- Day 23: Document context injection + async upload ✅
- Day 24: Intent classification overhaul (6000x latency improvement) ✅
- Day 25: Sentence-aware chunking + diversity filtering
- Day 26: Document deduplication
- Day 27: Pre-built llama-cpp-python wheel
- Day 28: Retrieval-confidence routing (post-rerank threshold)

---

# Future Improvements

* Celery-based async task queue
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
