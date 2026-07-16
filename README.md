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
* Full document lifecycle management, including duplicate prevention
* Running fully locally using containerized infrastructure

---

# Core Features

* Upload enterprise documents (PDF, DOCX, TXT)
* Automatic document parsing
* Async document processing — upload returns instantly
* Auto-generated document descriptions using LLM
* Document context injection — every chunk labeled with source
* Sentence-aware chunking — never splits mid-sentence or mid-word
* Content-hash based duplicate detection — re-uploading the same file skips reprocessing entirely
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
  |-- Document Upload (async, with dedup check)
  |        |
  |        v
  |    Read file bytes → SHA-256 hash → check DB for existing content_hash
  |        |                                   |
  |        |                          [match found]
  |        |                                   v
  |        |                    Return existing document, duplicate=true
  |        |                    (no disk write, no reprocessing)
  |        v [no match]
  |    Save file → DB record (status=processing, content_hash stored) → Return instantly
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
* llama-cpp-python (Phi-3-mini-4k-instruct-Q4_K_M, n_ctx=2048)
* PyMuPDF (layout-aware text extraction)
* python-docx

### Chunking

* Regex-based sentence splitting (no external NLP dependency)
* Sentences grouped up to ~500 chars per chunk
* 1-sentence overlap carried between chunks
* Never splits mid-sentence or mid-word
* Chunks rejoined with a space separator between sentences

### Deduplication

* SHA-256 hash computed over raw file bytes at upload time
* Checked against `documents.content_hash` before any disk write or processing
* Duplicate uploads return the existing document's record immediately (`duplicate: true`), skipping disk I/O, chunking, embedding, and LLM description generation entirely
* Deleting a document frees its hash for re-upload (row removal is sufficient — no separate cleanup needed)

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

## Housekeeping Pass (post-Day-25, pre-Day-26) — Bug Fixes

A verification pass against a fresh codebase upload surfaced several latent bugs that had drifted from the documented state. All fixed in this pass, none required a schema or architecture change:

- **`rag_service.py`**: `n_ctx` was still `4096` despite being documented as reduced to `2048` after the earlier `GGML_ASSERT` decode crash investigation. Corrected to `2048`.
- **`logger_service.py`**: two typos —
  - `logger.propogate=False` → `logger.propagate=False` (the misspelled version silently set a meaningless attribute; log propagation to the root logger was never actually being disabled).
  - `self.formatException(record.exec_info)` → `self.formatException(record.exc_info)` (the misspelled version would throw `AttributeError` the moment any log call carried real exception info).
- **`document_processor.py`**: the empty-text warning used `extra={"file_path": file_path}` instead of the correct nested shape `extra={"extra": {"file_path": file_path}}` used everywhere else in the codebase. The old shape silently dropped `file_path` from the JSON log output. Fixed.
- **`text_chunker.py`**: chunks were rejoined with `"".join(current_chunk)` instead of `" ".join(current_chunk)`. Since sentence splitting strips the original whitespace between sentences, this glued sentences together with no space at chunk boundaries — a likely contributor to the "missing space" artifact previously attributed solely to PyMuPDF. Fixed. Note: existing ingested chunks in the DB still reflect the old (unspaced) joining; only chunks generated from this point forward are affected by the fix. A full re-ingestion pass is needed to clean up existing data, same as after the Day 25 chunking rewrite — not done automatically as part of this fix since it's a destructive/bulk operation.
- **`api/routes/documents.py`**: removed the unused `db: Session = Depends(get_db)` dependency from `/search` and `/ask` — neither handler used it; it was opening and closing a wasted DB connection on every request to the two most frequently hit endpoints.
- Removed a stray file named `1` from the project root — an orphaned pre-Day-19 draft of `main.py` with no router, no Qdrant integration, and a raw-string `/documents` POST signature. Not referenced anywhere in the project and not part of the documented structure.

---

## Day 26 — Document Deduplication

Prevents re-uploading the same file content from creating duplicate chunks, vectors, and embedding/LLM cost.

Key implementations:

- Added `content_hash` column (`String`, indexed, nullable) to the `Document` model in `database/models.py`
- Manually migrated the live PostgreSQL table (`ALTER TABLE ... ADD COLUMN` + `CREATE INDEX`), since `create_all()` does not alter existing tables — same known gotcha documented back in Day 23 for `document_description`
- `upload_document` now reads the uploaded file's bytes once, computes a SHA-256 hash, and checks `documents.content_hash` for an existing match **before** writing anything to disk or queuing background processing
- On a match: returns the existing document's `id`/`file_name`/`status` immediately with `duplicate: true` — no disk write, no chunking, no embedding generation, no LLM description call
- On no match: proceeds exactly as before, now also persisting `content_hash` on the new row, and returns `duplicate: false`
- Deleting a document (existing Day 22 DELETE logic, unchanged) removes its row entirely, which correctly frees its hash for a legitimate future re-upload of the same file
- `sdk/example.py` updated to demonstrate the duplicate-upload path explicitly

Hashing choice: SHA-256 over file content (not filename) — catches the actual duplicate case (same bytes, any filename) without falsely flagging two different documents that happen to share a name. Kept distinct from the MD5 hashing already used in `embedding_service.py` for cache keys, which is a different, non-adversarial use case.

`content_hash` is intentionally **not** exposed via `GET /documents` or `GET /documents/{id}` — it's an internal dedup mechanism with no client-facing use, and exposing it would let a caller probe "does this exact file already exist" without uploading anything, for no benefit.

Known limitation: documents already in the database before this feature existed have `content_hash = NULL` and are not retroactively deduplicated — this only prevents new duplicates going forward. `NULL` values never match each other in the lookup query, so this poses no false-positive risk; it's simply a gap for pre-existing data, addressable later as a separate one-off backfill/audit if needed.

Verified end-to-end: uploading the same file twice returns the same `id` with `duplicate: true` on the second call, with no growth in `storage/documents/` or `document_chunks` row count; uploading a genuinely different file still returns `duplicate: false`.

---

## Day 27 — Faster, Cross-Platform Docker Builds

Goal: reduce Docker build time and keep it fast on any machine, not just the one it was first built on — not merely "build it once, fast, on my own laptop."

Initial approach considered and rejected: building a host-native `llama-cpp-python` wheel (`pip wheel llama-cpp-python --no-deps -w wheels/`) on the WSL2 host and reusing it in Docker. Rejected because such a wheel bakes in the *building* machine's CPU instruction set (AVX/AVX2/etc.) and glibc version — it would risk `SIGILL` crashes on a different machine's CPU, or fail entirely on an older glibc. This directly conflicts with the actual goal (works on any device), so it was not implemented.

Adopted approach: point `pip` at the official, portable prebuilt wheel indexes the respective projects publish for exactly this purpose:

- `llama-cpp-python`: `https://abetlen.github.io/llama-cpp-python/whl/cpu` — a generic-baseline CPU build (`py3-none-manylinux2014_x86_64`), not tied to a specific CPU's instruction set or even a specific Python minor version.
- `torch` (a transitive dependency of `sentence-transformers`, not explicit in `requirements.txt` but resolved anyway): `https://download.pytorch.org/whl/cpu` — PyTorch's own official CPU-only build (`torch-2.13.0+cpu`), avoiding the ~800MB-2GB+ CUDA/cuDNN runtime that gets pulled in by default even though this project never uses a GPU.

Both are added as `--extra-index-url` lines at the top of `requirements.txt` — no Dockerfile changes needed for pip to find them.

With both packages now installing from prebuilt wheels, the Dockerfile's `apt-get install -y gcc g++ cmake` layer was removed entirely — nothing in `requirements.txt` requires compilation anymore (`psycopg2-binary` is already binary; `numpy`, `scipy`, `scikit-learn`, `lxml`, `tokenizers`, `PyMuPDF` all publish manylinux wheels).

Verified, measured results (clean `--no-cache` build, same machine, before vs. after):

| | Before | After |
|---|---|---|
| Total build time | 955.3s (~16 min) | 254.5s (~4.2 min) — ~3.75x faster |
| `pip install` step | 552.6s | 169.9s — ~3.25x faster |
| Image export step | 397.1s | 81.6s — ~4.9x faster |
| Final image size | not previously measured | 2.22GB |

Also verified: an unchanged rebuild hits Docker's layer cache correctly and completes in ~2s, confirming the simplified Dockerfile still caches as expected.

Portability note: unlike a host-built wheel, both adopted wheels are official, generic manylinux/CPU builds with no host-specific optimization baked in — the same `requirements.txt` should produce the same fast, non-compiling build on any x86_64 Linux Docker host, not just the machine that happened to build it first.

Known follow-on, not yet done: the `torch` CPU wheel (~192MB) is still the single largest dependency download. No further action planned unless build time becomes a problem again — flagging only so a future thread doesn't rediscover this from scratch.

---

# API Reference

## Document Management

```
POST   /documents              Upload a document (async, returns instantly; duplicate content returns existing doc with duplicate=true)
GET    /documents              List all documents
GET    /documents/{id}         Get document by ID (poll for status: ready)
DELETE /documents/{id}         Delete document and all associated data (also frees its content hash for re-upload)
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

## Database migrations (manual)

`Base.metadata.create_all()` only creates missing tables — it never alters existing ones. Any time a new column is added to a model on a live database, run the equivalent of:

```bash
docker compose exec postgres psql -U admin -d knowledge_ai -c "ALTER TABLE documents ADD COLUMN IF NOT EXISTS <column> <type>;"
docker compose exec postgres psql -U admin -d knowledge_ai -c "CREATE INDEX IF NOT EXISTS ix_documents_<column> ON documents (<column>);"
```

(substituting the actual column name/type). This has already been needed twice — `document_description` (Day 23) and `content_hash` (Day 26) — and will be needed again for any future schema change.

---

## Upload a document

```bash
curl -X POST http://localhost:8000/documents \
  -F "file=@document.pdf"
```

Note: if using Swagger UI (`/docs`), clear the default `"string"` value in the `description` field before executing, or leave it blank.

Re-uploading the exact same file content returns the existing document immediately with `"duplicate": true` — no reprocessing occurs.

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
- Housekeeping pass: n_ctx regression, logger typos, extra= shape, chunk join separator, unused db deps, stray file removal ✅
- Day 26: Document deduplication ✅
- Day 27: Faster, cross-platform Docker builds (prebuilt CPU wheels for llama-cpp-python and torch, compiler toolchain removed) ✅
- Day 28: Retrieval-confidence routing (post-rerank threshold, calibrated on clean chunks)

---

# Known Non-Blocking Issues (carried forward)

- Occasional missing space between PDF text runs (e.g. `M.Sc.Computer`) — PyMuPDF extraction quirk; the chunk-join spacing fix (housekeeping pass) may have reduced this, not yet fully re-verified post-fix
- Rare `GGML_ASSERT` buffer-overflow crash on unusually long/complex queries (one observed occurrence, not reproducible on normal queries) — a preventive `n_batch=256` fix was proposed but not applied
- Embedding-based intent classifier (behind `INTENT_CLASSIFIER_ENABLED` toggle) is only 8/10 accurate and not used by default
- Pre-existing documents uploaded before Day 26 have `content_hash = NULL` and are not retroactively deduplicated
- FastAPI `BackgroundTasks` (not Celery) means an in-flight document processing job is lost if the backend restarts mid-processing

---

# Future Improvements

* Celery-based async task queue
* Fix PDF text-run spacing artifact (minor, re-verify after chunk-join fix)
* Web dashboard
* Observability dashboard (Grafana + Loki)
* Kubernetes deployment
* Multi-tenant architecture
* SDK pip-installable package
* Adaptive top-k retrieval
* Query rewriting / expansion
* Backfill/audit tool for pre-Day-26 duplicate documents

---

# Author

Ajmal
AI Engineer | MSc Artificial Intelligence & Machine Learning
