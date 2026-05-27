import json
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import Base, engine, get_db, SessionLocal
from app.models import Summary
from app.schemas import ArticleOut, SummaryRequest, SummaryResponse
from app.seed import load_teams, seed_database, validate_league
from app.services.news_service import get_articles
from app.services.summarizer import create_summary


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield


settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"name": settings.app_name, "status": "ok"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/source-status")
def source_status():
    live_news_enabled = bool(settings.news_api_key)
    return {
        "live_news_enabled": live_news_enabled,
        "article_source": "NewsAPI live search + SQLite cache" if live_news_enabled else "SQLite mock seed data only",
        "note": "Add NEWS_API_KEY in backend/.env for live article discovery. Scores and standings should come from a structured sports data API, not news articles."
    }


@app.get("/leagues")
def leagues():
    return ["NBA", "NFL"]


@app.get("/teams")
def teams(league: str = Query(...)):
    try:
        normalized = validate_league(league)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return load_teams()[normalized]


@app.get("/news", response_model=list[ArticleOut])
def news(
    league: str = Query(...),
    team: str = Query(...),
    range: str = Query("7d", alias="range"),
    db: Session = Depends(get_db),
):
    return get_articles(db=db, league=league, team=team, time_range=range)


@app.post("/summarize", response_model=SummaryResponse)
def summarize(payload: SummaryRequest, db: Session = Depends(get_db)):
    summary = create_summary(payload.league, payload.team, payload.articles)

    record = Summary(
        team_name=summary.team,
        league=summary.league,
        summary_text=summary.summary,
        topic_json=json.dumps([topic.model_dump(mode="json") for topic in summary.topics]),
        article_ids=json.dumps([article.id for article in payload.articles if article.id is not None]),
    )
    db.add(record)
    db.commit()

    return summary
