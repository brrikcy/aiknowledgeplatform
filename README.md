# Knowledge AI Platform

A **self-hosted AI knowledge platform** that allows organizations to upload internal documents and interact with them using **LLM-powered semantic search and Retrieval Augmented Generation (RAG)**.

The platform is designed to run **entirely inside an organization's infrastructure**, ensuring that sensitive company data never leaves their environment.

---

# Project Goal

The goal of this project is to build a **production-style AI infrastructure platform** capable of:

- Ingesting enterprise documents
- Storing document metadata
- Processing document content
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
- Semantic chunking and embedding generation
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
  │     Embeddings
  │
  ▼
Vector Database (Qdrant)
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

### AI / NLP (Planned)
- Sentence Transformers
- OpenAI / Local LLMs

### Document Processing (Planned)
- PyMuPDF
- python-docx
- pytesseract

### Infrastructure
- Docker
- Docker Compose

---

# Project Structure

```
knowledge-ai-platform
│
├── api
│   └── main.py            # FastAPI application
│
├── database
│   ├── db.py              # Database connection & session
│   └── models.py          # SQLAlchemy models
│
├── services               # Business logic (RAG, agents later)
│
├── storage
│   └── documents          # Uploaded files stored locally
│
├── scripts                # Utility scripts
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

## Day 3 — Database Models & Data Insertion

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

Example stored file:

```
storage/documents/2e4f9a-test.pdf
```

---

# Local Setup Instructions

## 1 Install dependencies

```
pip install -r requirements.txt
```

---

## 2 Start PostgreSQL using Docker

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

## 3 Run the backend server

```
uvicorn api.main:app --reload
```

---

## 4 Open API documentation

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

## Week 2 — Document Processing
- PDF parsing
- DOCX parsing
- text extraction
- document processing pipeline

## Week 3 — Embedding Pipeline
- semantic chunking
- embedding generation
- vector database integration

## Week 4 — RAG System
- vector search
- LLM integration
- question answering

## Week 5 — AI Agents & SDK
- agent tool execution
- Python SDK

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
