from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.services.clustering import NewsItem as NewsItemDC, cluster_news
from app.services.sentiment import rank_news
from app.database import get_db, engine
from app.models.news import NewsItem as NewsItemDB, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Forensic News Analyzer", version="0.1.0")


class NewsInput(BaseModel):
    id: str
    title: str
    text: str
    company: str | None = None
    location: str | None = None
    industry: str | None = None


class ClusterResult(BaseModel):
    company: str | None
    location: str | None
    industry: str | None
    count: int
    ids: list[str]


class SentimentResult(BaseModel):
    id: str
    title: str
    score: float
    label: str


class AnalyzeResult(BaseModel):
    clusters: list[ClusterResult]
    sentiment: list[SentimentResult]
    saved: int


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/cluster", response_model=list[ClusterResult])
def cluster(news: list[NewsInput]):
    if not news:
        raise HTTPException(status_code=400, detail="News list cannot be empty")
    items = [NewsItemDC(**n.model_dump()) for n in news]
    clusters = cluster_news(items)
    return [
        ClusterResult(
            company=c.company,
            location=c.location,
            industry=c.industry,
            count=len(c.items),
            ids=[i.id for i in c.items],
        )
        for c in clusters
    ]


@app.post("/sentiment", response_model=list[SentimentResult])
def sentiment(news: list[NewsInput]):
    if not news:
        raise HTTPException(status_code=400, detail="News list cannot be empty")
    items = [n.model_dump() for n in news]
    ranked = rank_news(items)
    return [
        SentimentResult(id=r.id, title=r.title, score=r.score, label=r.label)
        for r in ranked
    ]


@app.post("/analyze", response_model=AnalyzeResult)
def analyze(news: list[NewsInput], db: Session = Depends(get_db)):
    if not news:
        raise HTTPException(status_code=400, detail="News list cannot be empty")

    cluster_items = [NewsItemDC(**n.model_dump()) for n in news]
    clusters = cluster_news(cluster_items)

    cluster_map: dict[str, str] = {}
    for c in clusters:
        key = f"{c.company}|{c.location}|{c.industry}"
        for item in c.items:
            cluster_map[item.id] = key

    ranked = rank_news([n.model_dump() for n in news])
    sentiment_map = {r.id: r for r in ranked}

    for item in news:
        r = sentiment_map[item.id]
        db_item = NewsItemDB(
            id=item.id,
            title=item.title,
            text=item.text,
            company=item.company,
            location=item.location,
            industry=item.industry,
            sentiment_score=r.score,
            sentiment_label=r.label,
            cluster_key=cluster_map.get(item.id),
        )
        db.merge(db_item)
    db.commit()

    return AnalyzeResult(
        clusters=[
            ClusterResult(
                company=c.company,
                location=c.location,
                industry=c.industry,
                count=len(c.items),
                ids=[i.id for i in c.items],
            )
            for c in clusters
        ],
        sentiment=[
            SentimentResult(id=r.id, title=r.title, score=r.score, label=r.label)
            for r in ranked
        ],
        saved=len(news),
    )


@app.get("/news")
def get_news(db: Session = Depends(get_db)):
    return db.query(NewsItemDB).all()
