from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.services.clustering import NewsItem, cluster_news
from app.services.sentiment import rank_news

app = FastAPI(title="Forensic News Analyzer", version="0.1.0")


class NewsInput(BaseModel):
    id: str
    title: str
    text: str
    company: str | None = None
    location: str | None = None
    industry: str | None = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/cluster")
def cluster(news: list[NewsInput]):
    if not news:
        raise HTTPException(status_code=400, detail="News list cannot be empty")
    items = [NewsItem(**n.model_dump()) for n in news]
    clusters = cluster_news(items)
    return [
        {
            "company": c.company,
            "location": c.location,
            "industry": c.industry,
            "count": len(c.items),
            "ids": [i.id for i in c.items],
        }
        for c in clusters
    ]


@app.post("/sentiment")
def sentiment(news: list[NewsInput]):
    if not news:
        raise HTTPException(status_code=400, detail="News list cannot be empty")
    items = [n.model_dump() for n in news]
    ranked = rank_news(items)
    return [
        {
            "id": r.id,
            "title": r.title,
            "score": r.score,
            "label": r.label,
        }
        for r in ranked
    ]
