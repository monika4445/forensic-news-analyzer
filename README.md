# Forensic News Analyzer

A service for analyzing news background of Russian companies (.ru domain).

## Features

- News clustering by company, location, and industry
- Sentiment ranking (negative → positive scale)
- LLM-assisted PostgreSQL transaction error repair

## Stack

- Python 3.11
- FastAPI
- Docker / Docker Compose
- PostgreSQL

## Structure

```
app/
  api/        # FastAPI route handlers
  services/   # Business logic (clustering, sentiment)
  models/     # Pydantic schemas and DB models
docs/         # Architecture, capacity planning, implementation plan
```

## Docs

- [Tech Stack & Architecture](docs/architecture.md)
- [Capacity Planning](docs/capacity.md)
- [MVP Plan](docs/mvp_plan.md)
- [DB Error Repair Prompt](docs/db_prompt.md)

## Quick Start

```bash
docker-compose up --build
```

API available at `http://localhost:8000/docs`
