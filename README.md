# Knowledge AI Platform

A **self-hosted AI knowledge platform** that allows organizations to upload internal documents and interact with them using **LLM-powered semantic search and Retrieval Augmented Generation (RAG)**.

The platform runs **entirely inside the organization's infrastructure**, ensuring that sensitive company data never leaves their environment.

---

# Project Goal

The goal of this project is to build a **production-style AI infrastructure platform** capable of:

- Ingesting enterprise documents
- Extracting and processing document text
- Chunking documents for semantic retrieval
- Enabling semantic search over internal knowledge
- Supporting Retrieval Augmented Generation (RAG)
- Allowing AI agents to interact with company data
- Running fully locally using containerized infrastructure

This project also serves as a **hands-on learning journey for building real-world AI systems**, covering backend development, vector databases, RAG pipelines, and AI orchestration.

---

# Core Features (Planned)

- Upload enterprise documents (PDF, DOCX, TXT)
- Automatic document parsing
- Text extraction from documents
- Text chunking for retrieval
- Embedding generation
- Vector search using embeddings
- LLM-powered question answering
- AI agents interacting with enterprise knowledge
- Python SDK for developer integration
- Fully local deployment using Docker

---

# System Architecture (Planned)

```
Users
  │
  ▼
FastAPI Backend
  │
  ├── Document Upload
  │        │
  │        ▼
  │    Local Storage
  │        │
  │        ▼
  │    Text Extraction
  │        │
  │        ▼
  │      Chunking
  │        │
  │        ▼
  │    Embeddings
  │        │
  │        ▼
  │   Vector Database
  │
  ▼
Retrieval (RAG)
  │
  ▼
LLM Reasoning
  │
  ▼
Answers / AI Agents
```

---

# Technology Stack

### Backend
- Python
- FastAPI
- Pydantic

### Database
- PostgreSQL
- SQLAlchemy

### Vector Database (Planned)
- Qdrant

### AI / NLP
- PyMuPDF
- python-docx
- Sentence Transformers

### Infrastructure
- Docker
- Docker Compose

---

# Project Structure

```
knowledge-ai-platform
│
├── api
│   ├── main.py
│   └── routes
│        └── documents.py
│
├── database
│   ├── db.py
│   └── models.py
│
├── services
│   ├── document_processor.py
│   ├── text_chunker.py
│   └── embedding_service.py
│
├── storage
│   └── documents
│
├── scripts
│
├── requirements.txt
└── README.md
```

---

# Current Project Status

## Day 1 — Backend Setup

- Project repository created
- FastAPI backend initialized
- Swagger API documentation enabled

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

- PostgreSQL running via Docker
- SQLAlchemy database connection implemented
- Database connectivity verified

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

- SQLAlchemy Base model
- `documents` table
- Database session dependency
- API to insert document records

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

Capabilities:

- Create document records
- List stored documents
- Retrieve individual document metadata
- Delete documents

---

## Day 5 — Document Upload System

Implemented **real document upload functionality**.

Features added:

- File upload API
- Local document storage
- Unique filename generation using UUID
- File type validation

Allowed file types:

```
pdf
docx
txt
```

Uploaded files are stored in:

```
storage/documents/
```

---

## Day 6 — Document Text Extraction

Implemented the **document processing service**.

New capability:

- Extract text from uploaded documents

Supported formats:

```
PDF
DOCX
TXT
```

Pipeline implemented:

```
Upload Document
      ↓
Save File
      ↓
Extract Text
      ↓
Store Extracted Text in Database
```

---

## Day 7 — Text Chunking (RAG Preparation)

Implemented **text chunking for semantic retrieval**.

New table added:

```
document_chunks
```

Each document is split into multiple smaller pieces.

Pipeline now becomes:

```
Upload Document
      ↓
Extract Text
      ↓
Chunk Text
      ↓
Store Chunks in Database
```

Example:

```
Document → 5000 words
           ↓
Chunks → 10–15 smaller text blocks
```

This prepares the system for:

```
Embedding generation
Semantic search
RAG retrieval
```

---

## Day 8 — Embedding Generation

Implemented **vector embedding generation for document chunks**, enabling semantic search capabilities.

A new service was created to generate embeddings for each chunk using a transformer-based sentence embedding model.

New service:

```
services/embedding_service.py
```

Responsibilities:

- Load the embedding model
- Generate embeddings for text chunks
- Convert embeddings into JSON-serializable format

Embedding model used:

```
all-MiniLM-L6-v2
```

Embedding characteristics:

```
Vector dimension: 384
CPU-optimized inference
Designed for semantic similarity tasks
```

Updated ingestion pipeline:

```
Upload Document
      ↓
Save File
      ↓
Extract Text
      ↓
Chunk Text
      ↓
Generate Embedding for Each Chunk
      ↓
Store Chunks + Embeddings in Database
```

Database update:

The `document_chunks` table now includes an **embedding column**.

```
embedding (JSON)
```

Each chunk now stores its **384-dimension semantic vector representation**, enabling future implementation of:

```
Semantic similarity search
Vector retrieval
Retrieval Augmented Generation (RAG)
```

---

# Local Setup Instructions

## Install dependencies

```
pip install -r requirements.txt
```

---

## Start PostgreSQL using Docker

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

## Run the backend server

```
uvicorn api.main:app --reload
```

---

## Open API documentation

```
http://localhost:8000/docs
```

---

# Development Roadmap

## Week 1 — Backend Foundation
- FastAPI setup
- PostgreSQL integration
- Document CRUD APIs
- Document upload system
- Document text extraction
- Text chunking

## Week 2 — AI Retrieval Pipeline
- Embedding generation
- Vector database integration
- Semantic search

## Week 3 — RAG System
- Retrieval pipeline
- LLM integration
- question answering

## Week 4 — AI Agents
- tool-based agents
- orchestration layer

## Week 5 — Developer SDK
- Python client
- integration examples

## Week 6 — Production Setup
- Docker deployment
- Redis caching
- system optimization

---

# Future Improvements

- AI agent orchestration
- web dashboard
- observability (metrics & logs)
- Kubernetes deployment
- multi-tenant architecture

---

# Author

Ajmal  
AI Engineer | MSc Artificial Intelligence & Machine Learning
