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

This project is also designed as a **learning journey for building real-world AI systems**, covering backend engineering, vector databases, RAG pipelines, and AI orchestration.

---

# Core Features (Planned)

- Upload enterprise documents (PDF, DOCX, TXT)
- Automatic document parsing and processing
- Semantic chunking and embedding generation
- Vector search using embeddings
- LLM-powered question answering
- AI agents that can interact with company knowledge
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
│   └── main.py           # FastAPI application
│
├── database
│   └── db.py             # Database connection
│
├── services              # Business logic (RAG, agents later)
│
├── storage               # Uploaded documents
│
├── scripts               # Utility scripts
│
├── requirements.txt
└── README.md
```

---

# Current Project Status

## Day 1
- Project structure created
- FastAPI backend initialized
- API documentation available via Swagger

## Day 2
- PostgreSQL database running via Docker
- SQLAlchemy database connection implemented
- Database connectivity verified through `/db-test` endpoint

Example endpoint:

```
GET /db-test
```

Example response:

```
{"database":"connected"}
```

---

# Local Setup Instructions

## 1 Install dependencies

```
pip install -r requirements.txt
```

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

## 3 Run backend server

```
uvicorn api.main:app --reload
```

## 4 Open API documentation

```
http://localhost:8000/docs
```

---

# Development Roadmap

## Week 1
Backend foundation
- FastAPI setup
- PostgreSQL connection
- Document upload APIs

## Week 2
Document ingestion
- PDF/DOCX parsing
- text extraction
- document storage

## Week 3
Embedding pipeline
- chunking
- embedding generation
- vector database integration

## Week 4
RAG system
- vector search
- LLM integration
- question answering

## Week 5
AI agents and SDK

## Week 6
Docker deployment and system optimization

---

# Future Improvements

- AI agent orchestration
- UI dashboard
- observability (metrics/logging)
- Kubernetes deployment
- multi-tenant support

---

# Author

Ajmal  
AI Engineer | MSc Artificial Intelligence & Machine Learning





