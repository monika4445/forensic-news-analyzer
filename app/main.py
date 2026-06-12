from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from app.services.clustering import NewsItem as NewsItemDC, cluster_news
from app.services.sentiment import rank_news
from app.database import get_db, engine
from app.models.news import NewsItem as NewsItemDB, Base

try:
    Base.metadata.create_all(bind=engine)
except Exception:
    pass

app = FastAPI(title="Forensic News Analyzer", version="0.1.0")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


class NewsInput(BaseModel):
    id: str
    title: str
    text: str = ""
    company: str | None = None
    location: str | None = None
    industry: str | None = None

    @field_validator("id", "title")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be blank")
        return v.strip()


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
    db_status = "unavailable"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        pass
    return {"status": "ok", "database": db_status}


@app.post("/cluster", response_model=list[ClusterResult])
def cluster(news: list[NewsInput]):
    if not news:
        raise HTTPException(status_code=400, detail="News list cannot be empty")
    try:
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
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Clustering failed")


@app.post("/sentiment", response_model=list[SentimentResult])
def sentiment(news: list[NewsInput]):
    if not news:
        raise HTTPException(status_code=400, detail="News list cannot be empty")
    try:
        items = [n.model_dump() for n in news]
        ranked = rank_news(items)
        return [
            SentimentResult(id=r.id, title=r.title, score=r.score, label=r.label)
            for r in ranked
        ]
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Sentiment analysis failed")


@app.post("/analyze", response_model=AnalyzeResult)
def analyze(news: list[NewsInput], db: Session = Depends(get_db)):
    if not news:
        raise HTTPException(status_code=400, detail="News list cannot be empty")

    try:
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

    except OperationalError:
        db.rollback()
        raise HTTPException(status_code=503, detail="Database unavailable. Run: docker-compose up -d")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to save results")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Analysis failed")

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
    try:
        return db.query(NewsItemDB).all()
    except OperationalError:
        raise HTTPException(status_code=503, detail="Database unavailable. Run: docker-compose up -d")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Failed to retrieve news")
