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
* Allowing AI agents to interact with company data
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
* LLM-powered question answering
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
Semantic Retrieval
  |
  v
Context Builder
  |
  v
LLM (FLAN-T5)
  |
  v
Generated Answer
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
* HuggingFace Transformers
* PyTorch
* PyMuPDF
* python-docx

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
|   |-- rag_service.py
|   \-- qdrant_service.py
|
|-- storage
|   \-- documents
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
Upload Document
      |
      v
Save File
      |
      v
Extract Text
      |
      v
Store Extracted Text
```

---

## Day 7 — Text Chunking

Added table:

```
document_chunks
```

Pipeline:

```
Upload Document
      |
      v
Extract Text
      |
      v
Chunk Text
      |
      v
Store Chunks
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
Upload Document
      |
      v
Extract Text
      |
      v
Chunk Text
      |
      v
Generate Embeddings
      |
      v
Store Embeddings
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

Pipeline:

```
Question
   |
   v
Embedding
   |
   v
Chunk Retrieval
   |
   v
Context
   |
   v
LLM
   |
   v
Answer
```

---

## Day 11 — Vector Database Integration

Vector database:

```
Qdrant
```

Pipeline:

```
Question
   |
   v
Embedding
   |
   v
Qdrant Vector Search
   |
   v
Retrieve Chunks
   |
   v
Build Context
   |
   v
LLM
   |
   v
Answer
```

---

# Local Setup Instructions

## Install dependencies

```
pip install -r requirements.txt
```

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

* AI agent orchestration
* Web dashboard
* Observability (metrics & logs)
* Kubernetes deployment
* Multi-tenant architecture
* Hybrid retrieval (BM25 + vector search)

---

# Author

Ajmal
AI Engineer | MSc Artificial Intelligence & Machine Learning

