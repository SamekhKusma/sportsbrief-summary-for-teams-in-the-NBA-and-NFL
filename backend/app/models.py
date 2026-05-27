from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    league: Mapped[str] = mapped_column(String(20), index=True)
    team_name: Mapped[str] = mapped_column(String(120), index=True)
    title: Mapped[str] = mapped_column(String(300))
    source_name: Mapped[str] = mapped_column(String(120))
    source_url: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    published_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    content_snippet: Mapped[str] = mapped_column(Text, default="")
    article_hash: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Summary(Base):
    __tablename__ = "summaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    team_name: Mapped[str] = mapped_column(String(120), index=True)
    league: Mapped[str] = mapped_column(String(20), index=True)
    summary_text: Mapped[str] = mapped_column(Text)
    topic_json: Mapped[str] = mapped_column(Text)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    article_ids: Mapped[str] = mapped_column(Text, default="[]")
