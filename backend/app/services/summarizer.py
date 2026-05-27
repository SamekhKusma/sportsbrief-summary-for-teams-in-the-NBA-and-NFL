import re
from collections import defaultdict
from datetime import datetime
from typing import Any

from app.schemas import ArticleOut, SummaryResponse, TopicOut

CATEGORY_RULES: list[tuple[str, list[str]]] = [
    ("Injuries", ["injury", "injured", "questionable", "probable", "ankle", "knee", "hamstring", "limited", "recovery", "rehab", "soreness"]),
    ("Trades / roster moves", ["trade", "signing", "signed", "roster", "depth", "market", "free agent", "contract", "offseason"]),
    ("Game results", ["win", "loss", "defeated", "beat", "after win", "score", "late-game"]),
    ("Upcoming games", ["upcoming", "next game", "matchup", "schedule", "before the next"]),
    ("Coaching / front office", ["coach", "coaching", "front office", "staff", "officials"]),
    ("Player performance", ["performance", "praised", "production", "scoring", "defensive", "receiver", "quarterback", "two-way"]),
    ("Rumors", ["rumor", "rumors", "chatter", "linked", "connected", "monitoring"]),
]

NEGATIVE_WORDS = ["injury", "questionable", "limited", "soreness", "hamstring", "knee", "uncertain", "absence"]
POSITIVE_WORDS = ["praised", "positive", "win", "development", "earns praise", "on schedule", "optimism", "strong"]


def create_summary(league: str, team: str, articles: list[ArticleOut]) -> SummaryResponse:
    clean_articles = filter_team_articles(team, dedupe_input_articles(articles))

    if not clean_articles:
        return SummaryResponse(
            team=team,
            league=league,
            summary=f"No strong team-related news was found for {team} in the provided articles.",
            topics=[],
        )

    grouped: dict[str, list[ArticleOut]] = defaultdict(list)
    for article in clean_articles:
        grouped[categorize(article)].append(article)

    topics: list[TopicOut] = []
    category_order = [
        "Injuries",
        "Trades / roster moves",
        "Game results",
        "Upcoming games",
        "Coaching / front office",
        "Player performance",
        "Rumors",
        "Other",
    ]

    for category in category_order:
        category_articles = grouped.get(category, [])
        if not category_articles:
            continue
        topics.append(build_topic(category, category_articles))

    summary = build_team_summary(team, clean_articles, topics)

    return SummaryResponse(team=team, league=league, summary=summary, topics=topics)


def dedupe_input_articles(articles: list[ArticleOut]) -> list[ArticleOut]:
    seen: set[str] = set()
    unique: list[ArticleOut] = []
    for article in articles:
        key = article.source_url.lower().strip()
        if key in seen:
            continue
        seen.add(key)
        unique.append(article)
    return unique


def filter_team_articles(team: str, articles: list[ArticleOut]) -> list[ArticleOut]:
    team_lower = team.lower()
    filtered: list[ArticleOut] = []

    for article in articles:
        text = f"{article.team_name} {article.title} {article.description} {article.content_snippet}".lower()
        if article.team_name.lower() == team_lower or team_lower in text:
            filtered.append(article)

    return filtered


def categorize(article: ArticleOut) -> str:
    text = f"{article.title} {article.description} {article.content_snippet}".lower()

    for category, keywords in CATEGORY_RULES:
        if any(keyword in text for keyword in keywords):
            return category
    return "Other"


def build_topic(category: str, articles: list[ArticleOut]) -> TopicOut:
    primary = sorted(articles, key=lambda item: item.published_at, reverse=True)[0]
    text = f"{primary.title}. {primary.description or primary.content_snippet}".strip()

    return TopicOut(
        category=category,
        headline=make_headline(category, primary.title),
        summary=trim_words(clean_sentence(text), 75),
        importance=score_importance(category, articles),
        sentiment=score_sentiment(category, articles),
        sources=[
            {
                "title": article.title,
                "url": article.source_url,
                "source_name": article.source_name,
                "published_at": article.published_at.isoformat() if isinstance(article.published_at, datetime) else article.published_at,
            }
            for article in articles[:3]
        ],
    )


def make_headline(category: str, title: str) -> str:
    prefix_by_category = {
        "Injuries": "Injury update",
        "Trades / roster moves": "Roster update",
        "Game results": "Game result note",
        "Upcoming games": "Upcoming matchup note",
        "Coaching / front office": "Team leadership note",
        "Player performance": "Player performance note",
        "Rumors": "Rumor watch",
        "Other": "Team news",
    }
    return f"{prefix_by_category.get(category, 'Team news')}: {title}"


def score_importance(category: str, articles: list[ArticleOut]) -> int:
    base = {
        "Injuries": 4,
        "Trades / roster moves": 4,
        "Game results": 3,
        "Upcoming games": 3,
        "Coaching / front office": 3,
        "Player performance": 3,
        "Rumors": 2,
        "Other": 2,
    }.get(category, 2)

    if len(articles) >= 3:
        base += 1
    return min(base, 5)


def score_sentiment(category: str, articles: list[ArticleOut]) -> str:
    text = " ".join(f"{item.title} {item.description} {item.content_snippet}" for item in articles).lower()
    has_negative = any(word in text for word in NEGATIVE_WORDS)
    has_positive = any(word in text for word in POSITIVE_WORDS)

    if category == "Rumors":
        return "Mixed"
    if has_positive and has_negative:
        return "Mixed"
    if has_negative:
        return "Negative"
    if has_positive:
        return "Positive"
    return "Neutral"


def build_team_summary(team: str, articles: list[ArticleOut], topics: list[TopicOut]) -> str:
    if not topics:
        return f"No strong team-related news was found for {team} in the provided articles."

    topic_names = [topic.category.lower() for topic in topics[:3]]
    source_count = len(articles)
    topic_text = ", ".join(topic_names)
    summary = (
        f"{team} news is currently centered on {topic_text}. "
        f"The brief is based on {source_count} recent source item{'s' if source_count != 1 else ''}. "
        "Review the topic cards for source links and verification."
    )
    return trim_words(summary, 150)


def clean_sentence(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if text and not text.endswith((".", "!", "?")):
        text += "."
    return text


def trim_words(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]).rstrip(".,") + "."
