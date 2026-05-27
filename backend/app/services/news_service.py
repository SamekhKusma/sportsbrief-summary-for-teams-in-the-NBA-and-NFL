from datetime import datetime, timedelta
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import json

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Article
from app.seed import article_hash, is_valid_team, load_teams, validate_league

RANGE_TO_DELTA = {
    "24h": timedelta(hours=24),
    "3d": timedelta(days=3),
    "7d": timedelta(days=7),
}

NEWSAPI_ENDPOINT = "https://newsapi.org/v2/everything"


def get_articles(db: Session, league: str, team: str, time_range: str) -> list[Article]:
    try:
        league = validate_league(league)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not is_valid_team(league, team):
        raise HTTPException(status_code=400, detail="invalid team for selected league")

    if time_range not in RANGE_TO_DELTA:
        raise HTTPException(status_code=400, detail="range must be 24h, 3d, or 7d")

    cutoff = datetime.utcnow() - RANGE_TO_DELTA[time_range]

    # If NEWS_API_KEY exists, try live article discovery first.
    # If it fails, the app still works from SQLite seed/cache data.
    settings = get_settings()
    if settings.news_api_key:
        fetch_and_cache_newsapi_articles(db, league, team, cutoff, settings.news_api_key)

    articles = query_cached_articles(db, league, team, cutoff)

    # Seed data dates are fixed for portfolio demos. If the real current date moves
    # far beyond the seed window, fall back to the newest seed rows for that team.
    if not articles:
        articles = (
            db.query(Article)
            .filter(Article.league == league)
            .filter(Article.team_name == team)
            .order_by(Article.published_at.desc())
            .limit(10)
            .all()
        )

    return dedupe_articles(articles)


def query_cached_articles(db: Session, league: str, team: str, cutoff: datetime) -> list[Article]:
    return (
        db.query(Article)
        .filter(Article.league == league)
        .filter(Article.team_name == team)
        .filter(Article.published_at >= cutoff)
        .order_by(Article.published_at.desc())
        .limit(30)
        .all()
    )


def fetch_and_cache_newsapi_articles(db: Session, league: str, team: str, cutoff: datetime, api_key: str) -> None:
    team_info = get_team_info(league, team)
    nickname = team.split()[-1]
    abbreviation = team_info.get("abbreviation", "")

    aliases = [team]
    if abbreviation:
        aliases.append(f"{abbreviation} {nickname}")
    if league == "NBA" and team == "Oklahoma City Thunder":
        aliases.append("OKC Thunder")
    if league == "NBA" and team == "LA Clippers":
        aliases.append("Los Angeles Clippers")

    alias_query = " OR ".join(f'"{alias}"' for alias in aliases)
    query = f"({alias_query}) AND ({league} OR basketball OR football OR sports)"

    params = {
        "q": query,
        "from": cutoff.strftime("%Y-%m-%dT%H:%M:%S"),
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 30,
        "apiKey": api_key,
    }
    url = f"{NEWSAPI_ENDPOINT}?{urlencode(params)}"

    try:
        request = Request(url, headers={"User-Agent": "SportsBriefAI/1.0"})
        with urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return

    if payload.get("status") != "ok":
        return

    for item in payload.get("articles", []):
        source_url = item.get("url") or ""
        title = clean_text(item.get("title") or "")
        if not source_url or not title:
            continue

        description = clean_text(item.get("description") or "")
        content = clean_text(item.get("content") or "")

        if not is_strong_team_match(team, aliases, title, description, content):
            continue

        published_at = parse_newsapi_datetime(item.get("publishedAt"))
        source = item.get("source") or {}
        source_name = clean_text(source.get("name") or "Unknown source")

        article = Article(
            league=league,
            team_name=team,
            title=title[:300],
            source_name=source_name[:120],
            source_url=source_url[:500],
            published_at=published_at,
            description=description[:1000],
            content_snippet=content[:500],
            article_hash=article_hash(source_url, title),
        )

        try:
            db.add(article)
            db.commit()
        except IntegrityError:
            db.rollback()


def get_team_info(league: str, team: str) -> dict:
    for row in load_teams()[league]:
        if row["name"].lower() == team.lower():
            return row
    return {}


def parse_newsapi_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.utcnow()
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    return parsed.replace(tzinfo=None)


def clean_text(value: str) -> str:
    return " ".join(value.replace("\n", " ").split())


def is_strong_team_match(team: str, aliases: list[str], title: str, description: str, content: str) -> bool:
    haystack = f"{title} {description} {content}".lower()
    team_lower = team.lower()
    nickname = team.split()[-1].lower()

    if team_lower in haystack:
        return True

    for alias in aliases:
        if alias.lower() in haystack:
            return True

    # Allow nickname-only matches for distinctive team names, but avoid weak matches.
    weak_nicknames = {"giants", "jets", "kings", "magic", "nets", "rams", "spurs"}
    if nickname not in weak_nicknames and nickname in haystack:
        return True

    return False


def dedupe_articles(articles: list[Article]) -> list[Article]:
    seen: set[str] = set()
    unique: list[Article] = []

    for article in articles:
        key = article.article_hash or article.source_url.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(article)

    return unique
