import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_leagues(client):
    response = client.get("/leagues")
    assert response.status_code == 200
    assert response.json() == ["NBA", "NFL"]


def test_teams_for_nba(client):
    response = client.get("/teams", params={"league": "NBA"})
    assert response.status_code == 200
    teams = response.json()
    assert any(team["name"] == "Los Angeles Lakers" for team in teams)


def test_news_for_lakers(client):
    response = client.get("/news", params={"league": "NBA", "team": "Los Angeles Lakers", "range": "7d"})
    assert response.status_code == 200
    articles = response.json()
    assert len(articles) >= 1
    assert articles[0]["league"] == "NBA"


def test_summary_contract(client):
    news_response = client.get("/news", params={"league": "NFL", "team": "Kansas City Chiefs", "range": "7d"})
    assert news_response.status_code == 200

    response = client.post(
        "/summarize",
        json={
            "league": "NFL",
            "team": "Kansas City Chiefs",
            "articles": news_response.json(),
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["team"] == "Kansas City Chiefs"
    assert data["league"] == "NFL"
    assert "summary" in data
    assert isinstance(data["topics"], list)
    if data["topics"]:
        topic = data["topics"][0]
        assert 1 <= topic["importance"] <= 5
        assert topic["sentiment"] in ["Positive", "Negative", "Neutral", "Mixed"]
        assert len(topic["sources"]) >= 1
