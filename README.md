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
| Database | PostgreSQL + SQLAlchemy | Reliable, persistent storage for analyzed news |
| Containerization | Docker + Docker Compose | Reproducible environment, easy deployment |

No external paid APIs required — all NLP runs locally, data stays on-premises.

## Structure

```
app/
  main.py         # FastAPI app, routes, request/response models
  database.py     # SQLAlchemy engine and session
  services/       # Business logic (clustering, sentiment)
  models/         # SQLAlchemy DB models
docs/             # DB prompt for LLM-assisted error repair
tests/            # pytest — 27 tests (services + API endpoints)
```

## Capacity Planning

| Load | News/day | Avg processing time | Workers needed |
|------|----------|-------------------|----------------|
| Minimal | 100 | ~0.5s/news | 1 Celery worker |
| Medium | 10,000 | ~0.5s/news | 3-5 workers |
| High | 100,000+ | ~0.5s/news | 10+ workers + horizontal scaling |

- At 100 news/day: single server (2 CPU, 4GB RAM) is sufficient
- At 10k/day: 2-3 replicas behind a load balancer
- At 100k+/day: Kubernetes, autoscaling workers, read replicas for PostgreSQL

Storage estimate: ~2KB per news record → 100 news/day = ~70MB/year, 100k/day = ~70GB/year.

## MVP Plan

**Phase 1 — MVP (1-2 weeks)**
1. FastAPI app with `/ingest` and `/search` endpoints
2. News clustering service (by company, location, industry)
3. Sentiment ranking service (negative → positive score)
4. PostgreSQL schema for news storage
5. Docker Compose setup for local run

**Phase 2 — Production-ready (2-4 weeks)**
1. Celery + Redis for async background processing
2. News parser/scraper for .ru sources
3. Authentication and API keys
4. Logging, error handling, health checks
5. CI/CD pipeline (GitHub Actions)
6. Deploy to VPS or cloud (Docker Swarm or Kubernetes)

## Quick Start

**With Docker (all endpoints including DB):**
```bash
docker-compose up --build
```

**Local (cluster + sentiment endpoints only):**
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API available at `http://localhost:8000/docs`

## Tests

```bash
pytest tests/
```
