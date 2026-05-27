import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.models import Article

DATA_DIR = Path(__file__).parent / "data"
TEAMS_PATH = DATA_DIR / "teams.json"
SEED_ARTICLES_PATH = DATA_DIR / "seed_articles.json"


def load_teams() -> dict[str, list[dict[str, Any]]]:
    return json.loads(TEAMS_PATH.read_text(encoding="utf-8"))


def normalize_league(league: str) -> str:
    return league.strip().upper()


def validate_league(league: str) -> str:
    normalized = normalize_league(league)
    teams = load_teams()
    if normalized not in teams:
        raise ValueError("league must be NBA or NFL")
    return normalized


def is_valid_team(league: str, team_name: str) -> bool:
    teams = load_teams()
    return any(team["name"].lower() == team_name.lower() for team in teams.get(league, []))


def article_hash(source_url: str, title: str) -> str:
    raw = f"{source_url}|{title}".lower().encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def seed_database(db: Session) -> None:
    existing_count = db.query(Article).count()
    if existing_count > 0:
        return

    rows = json.loads(SEED_ARTICLES_PATH.read_text(encoding="utf-8"))
    for row in rows:
        article = Article(
            league=row["league"],
            team_name=row["team_name"],
            title=row["title"],
            source_name=row["source_name"],
            source_url=row["source_url"],
            published_at=datetime.fromisoformat(row["published_at"]),
            description=row.get("description", ""),
            content_snippet=row.get("content_snippet", ""),
            article_hash=article_hash(row["source_url"], row["title"]),
        )
        db.add(article)
    db.commit()
