from datetime import datetime, UTC
from sqlalchemy import String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class NewsItem(Base):
    __tablename__ = "news_items"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    text: Mapped[str] = mapped_column(String, default="")
    company: Mapped[str | None] = mapped_column(String, nullable=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    industry: Mapped[str | None] = mapped_column(String, nullable=True)
    sentiment_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    sentiment_label: Mapped[str | None] = mapped_column(String, nullable=True)
    cluster_key: Mapped[str | None] = mapped_column(String, nullable=True)
    analyzed_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
