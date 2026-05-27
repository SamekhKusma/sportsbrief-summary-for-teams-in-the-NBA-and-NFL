from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl

League = Literal["NBA", "NFL"]
TopicCategory = Literal[
    "Injuries",
    "Trades / roster moves",
    "Game results",
    "Upcoming games",
    "Coaching / front office",
    "Player performance",
    "Rumors",
    "Other",
]
Sentiment = Literal["Positive", "Negative", "Neutral", "Mixed"]


class Team(BaseModel):
    name: str
    abbreviation: str
    conference: str | None = None
    division: str | None = None


class ArticleOut(BaseModel):
    id: int | None = None
    league: League
    team_name: str
    title: str
    source_name: str
    source_url: str
    published_at: datetime
    description: str = ""
    content_snippet: str = ""

    model_config = {"from_attributes": True}


class SourceOut(BaseModel):
    title: str
    url: HttpUrl | str
    source_name: str
    published_at: datetime | str


class TopicOut(BaseModel):
    category: TopicCategory
    headline: str
    summary: str
    importance: int = Field(ge=1, le=5)
    sentiment: Sentiment
    sources: list[SourceOut]


class SummaryRequest(BaseModel):
    league: League
    team: str
    articles: list[ArticleOut]


class SummaryResponse(BaseModel):
    team: str
    league: League
    summary: str
    topics: list[TopicOut]
