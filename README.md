# Marginalia

Multi-tenant RAG (document Q&A) platform with citations, usage metering and a retrieval evaluation harness.

Each tenant uploads documents (e.g. security reports) and asks questions. Answers are grounded in, and cite (document and page), only that tenant's documents.

> **Status:** Phase 1 in progress. Document ingestion works; retrieval and answering are next. See the [roadmap](#roadmap).

## How it works

```
upload ─► parse pages ─► chunk (per page) ─► embed ─► store in Postgres + pgvector
question ─► embed ─► nearest-neighbour search ─► prompt Claude with top chunks ─► answer + citations
```

- **Page-aware chunking:** chunks never span pages, so every chunk maps to exactly one page number for citations.
- **Local embeddings:** `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions), no external embedding API.
- **Vector search:** pgvector with an HNSW index and cosine distance.
- **Answers:** Claude API, instructed to answer only from the retrieved chunks.

## Stack

Python 3.12, FastAPI, PostgreSQL + pgvector, SQLAlchemy 2, Alembic, `uv`, pytest, ruff.

## Quickstart

Requires Python 3.12+, [`uv`](https://docs.astral.sh/uv/) and Docker.

```bash
cp .env.example .env          # then set POSTGRES_PASSWORD (used by both Docker and the app)
uv sync
docker compose up -d --wait   # Postgres + pgvector on localhost:5434
uv run alembic upgrade head   # create tables
uv run uvicorn marginalia.main:app --reload
```

Interactive API docs: http://localhost:8000/docs

Upload a document:

```bash
curl -F "file=@report.pdf" http://localhost:8000/documents
```

Supported formats: PDF (with a text layer; scanned PDFs need OCR and are rejected), `.txt`, `.md`.

Run commands from the project root, since `.env` is read from the current directory.

## Development

```bash
uv run pytest          # tests marked `db` are skipped if Postgres isn't running
uv run ruff check .
uv run ruff format .
```

## Roadmap

- [ ] Phase 1: Single-tenant RAG with citations (ingestion done; retrieval, answering and end-to-end tests in progress)
- [ ] Phase 2: Multi-tenancy, auth, cross-tenant leakage test
- [ ] Phase 3: Queue ingestion, metering, tracing
- [ ] Phase 4: Evaluation harness, hybrid search, reranking (measure top-5 accuracy before/after)
- [ ] Phase 5: Deploy, architecture diagram, demo video
