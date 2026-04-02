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
* Fully local AI inference
* Containerized infrastructure

---

# System Architecture

```
Users
  |
  v
FastAPI Backend
  |
  |-- Document Upload
  |        |
  |        v
  |    Local Storage
  |        |
  |        v
  |    Text Extraction
  |        |
  |        v
  |      Chunking
  |        |
  |        v
  |   Embedding Generation
  |        |
  |        v
  |    Vector Database (Qdrant)
  |
  v
User Query
  |
  v
[LOG] request started (request_id)
  |
  v
Intent Classification (LLM)
  |
[LOG] intent classified (duration_ms)
  |
  |-- out_of_scope → Fixed Response
  |
  \-- knowledge_base_query
        |
        v
Hybrid Search (Vector + BM25 + RRF)
        |
[LOG] hybrid search completed (results_count, duration_ms)
        |
        v
Cross-Encoder Reranking
        |
[LOG] reranking completed (results_count, duration_ms)
        |
        v
Build Optimized Context
        |
        v
Generate Answer (LLM)
        |
[LOG] request completed (all stage timings, total_ms)
        |
        v
Response to Client
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
|   \-- qdrant_service.py
|
|-- storage
|   \-- documents
|
|-- models
|   \-- Phi-3-mini-4k-instruct-Q4_K_M.gguf
|
|-- scripts
|
|-- requirements.txt
\-- README.md
```

---

# Current Project Status

## Day 1 — Backend Setup

* Project repository created
* FastAPI backend initialized
* Swagger API documentation enabled

Endpoint:

```
GET /
```

Response:

```
{"status": "running"}
```

---

## Day 2 — Database Integration

* PostgreSQL running via Docker
* SQLAlchemy database connection implemented
* Database connectivity verified

Endpoint:

```
GET /db-test
```

Response:

```
{"database": "connected"}
```

---

## Day 3 — Database Models

Implemented:

* SQLAlchemy Base model
* documents table
* Database session dependency
* API to insert document records

Endpoint:

```
POST /documents
```

---

## Day 4 — Document CRUD APIs

Implemented full CRUD operations for document metadata.

Endpoints:

```
POST   /documents
GET    /documents
GET    /documents/{document_id}
DELETE /documents/{document_id}
```

---

## Day 5 — Document Upload System

Implemented real document upload functionality.

Allowed file types:

```
pdf
docx
txt
```

Storage location:

```
storage/documents/
```

---

## Day 6 — Document Text Extraction

Supported formats:

```
PDF
DOCX
TXT
```

Pipeline:

```
Upload Document → Save File → Extract Text → Store Extracted Text
```

---

## Day 7 — Text Chunking

Added table:

```
document_chunks
```

Pipeline:

```
Upload Document → Extract Text → Chunk Text → Store Chunks
```

---

## Day 8 — Embedding Generation

Model:

```
all-MiniLM-L6-v2
```

Vector size:

```
384
```

Pipeline:

```
Upload Document → Extract Text → Chunk Text → Generate Embeddings → Store Embeddings
```

---

## Day 9 — Semantic Search Prototype

Endpoint:

```
POST /search
```

Pipeline:

```
Query -> Embedding -> Cosine Similarity -> Top Chunks
```

---

## Day 10 — Retrieval Augmented Generation

Model:

```
google/flan-t5-base
```

Endpoint:

```
POST /ask
```

---

## Day 11 — Vector Database Integration

Vector database:

```
Qdrant
```

Pipeline:

```
Question → Embedding → Qdrant Vector Search → Retrieve Chunks → Build Context → LLM → Answer
```

---

## Day 12 — Retrieval Optimization and Context Engineering

Key improvements:

- Removed PostgreSQL dependency from retrieval pipeline
- Switched to fully vector-based retrieval using Qdrant payloads
- Stored chunk text directly inside Qdrant payload
- Eliminated redundant database queries during search
- Implemented score-based filtering of retrieved chunks
- Improved prompt engineering for better answer quality

---

## Day 13 — Hybrid Search (BM25 + Vector)

Implemented hybrid retrieval combining semantic vector search with keyword-based BM25 search using Reciprocal Rank Fusion.

Key implementations:

- Added BM25 keyword search service using rank_bm25
- BM25 retriever pulls chunk corpus from Qdrant (no PostgreSQL dependency)
- Created hybrid search service with Reciprocal Rank Fusion (RRF, k=60)
- Rewired /search and /ask endpoints to use hybrid retrieval

New files:

```
services/bm25_service.py
services/hybrid_search.py
```

---

## Day 14 — Better LLM

Replaced the weak flan-t5-base model with a production-capable local LLM.

Key changes:

- Replaced google/flan-t5-base with Phi-3-mini-4k-instruct-Q4_K_M
- Switched from HuggingFace Transformers to llama-cpp-python for inference
- Model runs fully on CPU via GGUF quantization (~2.2GB, 4-bit)
- Used create_chat_completion API for correct prompt formatting
- Removed transformers and torch dependencies

Model:

```
Phi-3-mini-4k-instruct-Q4_K_M.gguf
```

Inference stack:

```
llama-cpp-python → GGUF → CPU inference
```

---

## Day 15 — Reranking

Added cross-encoder reranking stage between hybrid search and LLM generation.

Key implementations:

- Created reranker_service.py using cross-encoder/ms-marco-MiniLM-L-6-v2
- Cross-encoder scores each (query, chunk) pair jointly for fine-grained relevance
- Hybrid search retrieves top-5 candidates, reranker selects top-3
- rerank_score added to each chunk for visibility and debugging

New file:

```
services/reranker_service.py
```

Reranking model:

```
cross-encoder/ms-marco-MiniLM-L-6-v2
```

---

## Day 16 — AI Agent (Intent Classification + Tool Routing)

Added a tool-routing agent layer that classifies user intent before running the retrieval pipeline.

Key implementations:

- Created agent_service.py with intent classifier and tool router
- LLM classifies each query into knowledge_base_query or out_of_scope
- knowledge_base_query routes through full hybrid search + rerank + LLM pipeline
- out_of_scope returns a fixed response with zero retrieval overhead
- Same Phi-3-mini instance reused for both classification and generation
- Classification uses temperature=0.0 and max_tokens=10 for deterministic fast output

New file:

```
services/agent_service.py
```

Agent routing:

```
User Query
      ↓
Intent Classification (Phi-3-mini, temp=0.0)
      ↓
┌─────────────────────────────────────┐
│ knowledge_base_query                │
│   → hybrid search + rerank + LLM   │
├─────────────────────────────────────┤
│ out_of_scope                        │
│   → fixed response, no retrieval   │
└─────────────────────────────────────┘
```

---

## Day 17 — Streaming Responses

Added token-by-token streaming of LLM responses via Server-Sent Events.

Key implementations:

- Added generate_answer_stream() to rag_service.py using stream=True
- Added run_agent_stream() to agent_service.py
- Added POST /ask/stream endpoint using FastAPI StreamingResponse
- Streaming is additive — existing POST /ask endpoint unchanged

New endpoint:

```
POST /ask/stream
```

---

## Day 18 — Observability (Structured Logging + Request Tracing)

Added production-grade structured JSON logging with per-request tracing and per-stage timing.

Key implementations:

- Created logger_service.py with JSONFormatter and get_logger factory
- Every request assigned a UUID request_id for cross-service log correlation
- Per-stage timing logged for: intent classification, hybrid search, reranking, LLM generation
- Total request duration logged on completion
- WARNING level logged when no relevant documents found
- Removed debug print statements from vector_search.py
- No new dependencies — uses Python built-in logging module

New file:

```
services/logger_service.py
```

Sample log output:

```json
{"timestamp": "...", "level": "INFO", "logger": "agent_service", "message": "request started", "request_id": "...", "query": "..."}
{"timestamp": "...", "level": "INFO", "logger": "agent_service", "message": "intent classified", "request_id": "...", "intent": "knowledge_base_query", "duration_ms": 18069}
{"timestamp": "...", "level": "INFO", "logger": "agent_service", "message": "hybrid search completed", "request_id": "...", "results_count": 5, "duration_ms": 572}
{"timestamp": "...", "level": "INFO", "logger": "agent_service", "message": "reranking completed", "request_id": "...", "results_count": 3, "duration_ms": 561}
{"timestamp": "...", "level": "INFO", "logger": "agent_service", "message": "request completed", "request_id": "...", "intent_ms": 18069, "search_ms": 572, "rerank_ms": 561, "llm_ms": 77203, "total_ms": 96407}
```

Known bottleneck identified via logging:

```
Intent Classification:  18,069ms  ← long prompt prefill on CPU
Hybrid Search:             572ms
Reranking:                 561ms
LLM Generation:         77,203ms  ← expected on CPU, mitigated by streaming
Total:                  96,407ms
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

## Install dependencies

```
pip install -r requirements.txt
```

---

## Download LLM

Create the models directory and download the LLM:

```
mkdir -p models
cd models
wget https://huggingface.co/bartowski/Phi-3-mini-4k-instruct-GGUF/resolve/main/Phi-3-mini-4k-instruct-Q4_K_M.gguf
cd ..
```

Note: The embedding model (all-MiniLM-L6-v2) and reranking model (ms-marco-MiniLM-L-6-v2) are downloaded automatically by sentence-transformers on first run. No manual step required.

---

## Start PostgreSQL

```
docker run -d \
  --name knowledge-postgres \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=admin123 \
  -e POSTGRES_DB=knowledge_ai \
  -p 5432:5432 \
  postgres:15
```

---

## Start Qdrant

```
docker run -d \
  --name knowledge-qdrant \
  -p 6333:6333 \
  qdrant/qdrant
```

---

## Run backend

```
uvicorn api.main:app --reload
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

* Docker deployment
* Redis caching
* System optimization

---

# Future Improvements

* Improved chunking strategy (sentence-aware, semantic chunking)
* Shorten intent classification prompt to reduce prefill latency
* Multi-tool agent with full ReAct loop (requires stronger LLM)
* Web dashboard
* Kubernetes deployment
* Multi-tenant architecture

---

# Author

Ajmal
AI Engineer | MSc Artificial Intelligence & Machine Learning
