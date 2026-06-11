# Forensic News Analyzer

A service for analyzing news background of Russian companies (.ru domain).

## Features

- News clustering by company, location, and industry
- Sentiment ranking (negative → positive scale)
- LLM-assisted PostgreSQL transaction error repair

## Stack

| Layer | Technology | Reason |
|-------|-----------|--------|
| API | FastAPI | Async, high performance, built-in OpenAPI docs |
| Language | Python 3.11 | Best ecosystem for NLP and data processing |
| Database | PostgreSQL | Reliable, supports JSONB for flexible news metadata |
| Cache / Queue | Redis | Async task queue via Celery |
| Containerization | Docker + Docker Compose | Reproducible environment, easy deployment |
| NLP | scikit-learn, sentence-transformers | Free, runs locally, no external API needed |
| Task Queue | Celery | Background processing of news ingestion |

No external paid APIs required — all NLP runs locally, data stays on-premises.

## Structure

```
app/
  api/        # FastAPI route handlers
  services/   # Business logic (clustering, sentiment)
  models/     # Pydantic schemas and DB models
docs/         # Capacity planning, MVP plan, DB prompt
```

## Quick Start

```bash
docker-compose up --build
```

API available at `http://localhost:8000/docs`
