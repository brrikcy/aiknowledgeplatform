# Knowledge AI Platform

A **self-hosted AI knowledge platform** that allows organizations to upload internal documents and interact with them using **LLM-powered semantic search and Retrieval Augmented Generation (RAG)**.

The platform runs **entirely inside the organization's infrastructure**, ensuring that sensitive company data never leaves their environment.

---

# Project Goal

The goal of this project is to build a **production-style AI infrastructure platform** capable of:

* Ingesting enterprise documents
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
* Text extraction from documents
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
  |    Local Storage (mounted volume)
  |        |
  |        v
  |    Text Extraction → Chunking → Embeddings
  |        |
  |        v
  |    PostgreSQL (metadata) + Qdrant (vectors)
  |        |
  |        v
  |    Invalidate BM25 cache (Redis)
  |
  |-- Document Delete
  |        |
  |        v
  |    Delete from Qdrant (vectors)
  |    Delete from PostgreSQL (metadata + chunks)
  |    Delete from disk (file)
  |    Invalidate BM25 cache (Redis)
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
              |
              v
   Cross-Encoder Reranking
              |
              v
      Build Optimized Context
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
* llama-cpp-python
* PyMuPDF
* python-docx

### Retrieval

* rank_bm25 (BM25Okapi)
* Reciprocal Rank Fusion
* Cross-Encoder Reranking

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

## Days 1-21 — (See previous entries)

All prior days complete. Full stack running with PostgreSQL, Qdrant, Redis, and FastAPI backend containerized via Docker Compose. Python SDK implemented. Redis caching for BM25 and embeddings verified.

---

## Day 22 — Fix DELETE Endpoint (Full Cleanup)

Fixed the document deletion endpoint to properly clean up all data stores.

Problem: The old DELETE endpoint only removed the PostgreSQL document record. Qdrant vectors, PostgreSQL chunk records, and the file on disk were left behind — deleted documents continued appearing in search results indefinitely.

Key fixes:

- Query all DocumentChunk records for the document before deletion
- Delete corresponding vectors from Qdrant using PointIdsList
- Delete the file from disk using os.remove
- Delete chunk records from PostgreSQL explicitly
- Call invalidate_bm25_cache() after deletion so BM25 index is rebuilt on next query
- Added PointIdsList import from qdrant_client.http.models

Delete now cleans up in this order:

```
1. Qdrant vectors deleted (PointIdsList)
2. File deleted from disk
3. DocumentChunk records deleted from PostgreSQL
4. Document record deleted from PostgreSQL
5. BM25 cache invalidated in Redis
```

Verified end-to-end: upload → search returns results → delete → search returns empty.

---

# API Reference

## Document Management

```
POST   /documents              Upload a document
GET    /documents              List all documents
GET    /documents/{id}         Get document by ID
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

## Open API docs

```
http://localhost:8000/docs
```

---

## Use the Python SDK

```
python -m sdk.example
```

---

# Development Roadmap

### Week 1 — Backend Foundation ✅
### Week 2 — AI Retrieval Pipeline ✅
### Week 3 — RAG System ✅
### Week 4 — AI Agents ✅
### Week 5 — Developer SDK ✅
### Week 6 — Production Setup ✅

---

# Optimization Roadmap

- Day 22: Fix DELETE endpoint ✅
- Day 23: Remove unused db deps + dead code cleanup
- Day 24: Shorten intent classification prompt
- Day 25: Sentence-aware chunking
- Day 26: Document deduplication

---

# Future Improvements

* Improved chunking strategy (sentence-aware, semantic chunking)
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
