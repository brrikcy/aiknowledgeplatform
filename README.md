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
* Running fully locally using containerized infrastructure

This project also serves as a **hands-on learning journey for building real-world AI systems**, covering backend development, vector databases, RAG pipelines, and AI orchestration.

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
* Redis caching for BM25 index (invalidated on upload) and embeddings (TTL 1hr)
* Full Docker Compose stack (PostgreSQL + Qdrant + Redis + Backend)
* Fully local AI inference
* Containerized infrastructure

---

# System Architecture

```
Users
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
  |    Text Extraction
  |        |
  |        v
  |      Chunking
  |        |
  |        v
  |   Embedding Generation
  |     (check Redis cache first)
  |        |
  |        v
  |    Qdrant (Docker) ←→ PostgreSQL (Docker)
  |        |
  |        v
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
* Python built-in logging module

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

## Day 1 — Backend Setup

* Project repository created
* FastAPI backend initialized
* Swagger API documentation enabled

---

## Day 2 — Database Integration

* PostgreSQL running via Docker
* SQLAlchemy database connection implemented

---

## Day 3 — Database Models

* documents and document_chunks tables
* SQLAlchemy Base model

---

## Day 4 — Document CRUD APIs

```
POST   /documents
GET    /documents
GET    /documents/{document_id}
DELETE /documents/{document_id}
```

---

## Day 5 — Document Upload System

Allowed file types: `pdf / docx / txt`

---

## Day 6 — Document Text Extraction

Pipeline: `Upload → Save → Extract Text → Store`

---

## Day 7 — Text Chunking

Character-level sliding window chunking (size=500, overlap=50).

---

## Day 8 — Embedding Generation

Model: `all-MiniLM-L6-v2` — Vector size: 384

---

## Day 9 — Semantic Search Prototype

```
POST /search
Query → Embedding → Cosine Similarity → Top Chunks
```

---

## Day 10 — Retrieval Augmented Generation

Initial RAG pipeline with `google/flan-t5-base`.

---

## Day 11 — Vector Database Integration

Qdrant for vector storage. Chunk text stored in payload. PostgreSQL removed from retrieval path.

---

## Day 12 — Retrieval Optimization and Context Engineering

- Removed PostgreSQL from retrieval pipeline entirely
- Score-based filtering, improved prompt engineering

---

## Day 13 — Hybrid Search (BM25 + Vector)

- BM25 retriever over Qdrant corpus
- Reciprocal Rank Fusion (RRF, k=60)

New files: `services/bm25_service.py`, `services/hybrid_search.py`

---

## Day 14 — Better LLM

- Replaced flan-t5-base with Phi-3-mini-4k-instruct-Q4_K_M
- llama-cpp-python for CPU inference

Model: `Phi-3-mini-4k-instruct-Q4_K_M.gguf`

---

## Day 15 — Reranking

- Cross-encoder reranking after hybrid search
- Hybrid retrieves top-5, reranker selects top-3

New file: `services/reranker_service.py`
Model: `cross-encoder/ms-marco-MiniLM-L-6-v2`

---

## Day 16 — AI Agent (Intent Classification + Tool Routing)

- Intent classifier routes to knowledge_base_query or out_of_scope
- /ask delegates entirely to run_agent()

New file: `services/agent_service.py`

---

## Day 17 — Streaming Responses

- generate_answer_stream() and run_agent_stream() added
- POST /ask/stream endpoint via FastAPI StreamingResponse

---

## Day 18 — Observability (Structured Logging + Request Tracing)

- JSONFormatter logger, UUID request_id per request
- Per-stage timing across full pipeline

New file: `services/logger_service.py`

---

## Day 19 — Docker Compose (Full Stack Containerization)

- Dockerfile for FastAPI backend
- docker-compose.yml with PostgreSQL + Qdrant + Backend
- Healthchecks, named volumes, dependency ordering
- Environment variables via .env

New files: `Dockerfile`, `docker-compose.yml`, `.env`, `.dockerignore`

---

## Day 20 — Redis Caching + Configuration Hardening

Added Redis caching for BM25 index and query embeddings. Also moved model path to environment variable.

Key implementations:

- Added Redis 7 service to docker-compose.yml with healthcheck and persistent volume
- Created cache_service.py with Redis client and get/set/delete helpers
- BM25 index serialized with pickle and cached in Redis after first build
- BM25 cache invalidated automatically on every document upload
- Query embeddings cached by MD5 hash of query string with 1hr TTL
- Silent cache failure — if Redis is down, system falls back to fresh computation
- Moved MODEL_PATH to environment variable — no longer hardcoded in rag_service.py
- models/ added to .gitignore — GGUF file never tracked in git
- Verified: search_ms dropped from 858ms to 217ms on cache hit (4x improvement)

New file:

```
services/cache_service.py
```

Cache behavior:

```
First request:
  embedding cache miss → generate → cache (TTL 1hr)
  BM25 cache miss → rebuild index → cache (no TTL)

Second request (same query):
  embedding cache hit → instant
  BM25 cache hit → instant

On document upload:
  BM25 cache invalidated → rebuilt on next query
```

---

# API Reference

## Document Management

```
POST   /documents              Upload a document
GET    /documents              List all documents
GET    /documents/{id}         Get document by ID
DELETE /documents/{id}         Delete document by ID
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

# Development Roadmap

### Week 1 — Backend Foundation

* FastAPI
* PostgreSQL
* Upload system
* Text extraction
* Chunking

### Week 2 — AI Retrieval Pipeline

* Embeddings
* Vector database
* Semantic search

### Week 3 — RAG System

* Retrieval pipeline
* LLM integration
* Hybrid search

### Week 4 — AI Agents

* Tool-based agents
* Orchestration layer

### Week 5 — Developer SDK

* Python client
* Integration examples

### Week 6 — Production Setup

* Docker deployment ✅
* Redis caching ✅
* System optimization

---

# Future Improvements

* Improved chunking strategy (sentence-aware, semantic chunking)
* Multi-tool agent with full ReAct loop (requires stronger LLM)
* Web dashboard
* Observability dashboard (Grafana + Loki)
* Kubernetes deployment
* Multi-tenant architecture

---

# Author

Ajmal
AI Engineer | MSc Artificial Intelligence & Machine Learning
