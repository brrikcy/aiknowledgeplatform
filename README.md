# Knowledge AI Platform

A **self-hosted AI knowledge platform** that allows organizations to upload internal documents and interact with them using **LLM-powered semantic search and Retrieval Augmented Generation (RAG)**.

The system runs **entirely inside the organization's infrastructure**, ensuring that sensitive company data never leaves their environment.

---

# Project Goal

The goal of this project is to build a **production-style AI infrastructure system** that enables:

- Document ingestion
- Semantic search over documents
- Retrieval Augmented Generation (RAG)
- AI agents for knowledge interaction
- Local deployment inside company infrastructure

This project also serves as a **hands-on learning journey for building real-world AI systems**, covering backend engineering, vector databases, RAG pipelines, and AI orchestration.

---

# Core Features (Planned)

- Upload enterprise documents (PDF, DOCX, TXT)
- Automatic document parsing and processing
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
  ├── Document Processing
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
├── storage                # Uploaded documents
│
├── scripts                # Utility scripts
│
├── requirements.txt
└── README.md
```

---

# Current Project Status

## Day 1 – Backend Setup
- Project repository created
- FastAPI backend initialized
- Swagger API documentation enabled

Available endpoint:

```
GET /
```

Response:

```
{"status": "running"}
```

---

## Day 2 – Database Integration

- PostgreSQL running via Docker
- SQLAlchemy database connection implemented
- Database connectivity verified

Test endpoint:

```
GET /db-test
```

Response:

```
{"database": "connected"}
```

---

## Day 3 – Database Models & Data Insertion

Implemented:

- SQLAlchemy Base model
- `documents` table
- database session dependency
- API to insert document records

Endpoint:

```
POST /documents
```

Example request:

```
file_name = policy.pdf
storage_path = storage/policy.pdf
```

Example response:

```
{
  "id": "uuid-value",
  "file_name": "policy.pdf",
  "status": "uploaded"
}
```

Data is successfully stored in PostgreSQL.

---

# Local Setup Instructions

## 1 Install dependencies

```
pip install -r requirements.txt
```

---

## 2 Start PostgreSQL with Docker

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

## Week 1 – Backend Foundation
- FastAPI setup
- PostgreSQL integration
- Document CRUD APIs

## Week 2 – Document Processing
- PDF/DOCX parsing
- text extraction
- document storage

## Week 3 – Embedding Pipeline
- semantic chunking
- embedding generation
- vector database integration

## Week 4 – RAG System
- vector search
- LLM integration
- question answering

## Week 5 – AI Agents & SDK
- agent tool execution
- Python SDK

## Week 6 – Production Setup
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
