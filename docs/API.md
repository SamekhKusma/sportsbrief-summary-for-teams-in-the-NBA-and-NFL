# API Documentation

Base URL for local development:

```text
http://localhost:8000
```

## GET /

Returns app metadata.

### Response

```json
{
  "name": "SportsBrief AI",
  "status": "ok"
}
```

## GET /health

Returns backend health status.

### Response

```json
{
  "status": "healthy"
}
```

## GET /leagues

Returns supported leagues.

### Response

```json
["NBA", "NFL"]
```

## GET /teams

Returns all teams for a league.

### Query parameters

| Name | Type | Required | Example |
|---|---|---:|---|
| league | string | yes | NBA |

### Example

```text
GET /teams?league=NBA
```

## GET /news

Returns recent filtered articles for one team.

### Query parameters

| Name | Type | Required | Example |
|---|---|---:|---|
| league | string | yes | NBA |
| team | string | yes | Los Angeles Lakers |
| range | string | yes | 7d |

Allowed ranges:

- 24h
- 3d
- 7d

### Example

```text
GET /news?league=NBA&team=Los%20Angeles%20Lakers&range=7d
```

## POST /summarize

Creates a strict JSON team brief from article metadata.

### Request

```json
{
  "league": "NBA",
  "team": "Los Angeles Lakers",
  "articles": [
    {
      "id": 1,
      "league": "NBA",
      "team_name": "Los Angeles Lakers",
      "title": "Lakers guard listed as questionable with ankle soreness",
      "source_name": "Mock Sports Wire",
      "source_url": "https://example.com/nba/lakers-guard-questionable-ankle",
      "published_at": "2026-05-24T10:00:00",
      "description": "Los Angeles listed a rotation guard as questionable before the next matchup because of ankle soreness.",
      "content_snippet": "The Lakers have not ruled him out, but the injury report makes his availability uncertain."
    }
  ]
}
```

### Response

```json
{
  "team": "Los Angeles Lakers",
  "league": "NBA",
  "summary": "Los Angeles Lakers news is currently centered on injuries.",
  "topics": [
    {
      "category": "Injuries",
      "headline": "Injury update: Lakers guard listed as questionable with ankle soreness",
      "summary": "Lakers guard listed as questionable with ankle soreness. Los Angeles listed a rotation guard as questionable before the next matchup because of ankle soreness.",
      "importance": 4,
      "sentiment": "Negative",
      "sources": [
        {
          "title": "Lakers guard listed as questionable with ankle soreness",
          "url": "https://example.com/nba/lakers-guard-questionable-ankle",
          "source_name": "Mock Sports Wire",
          "published_at": "2026-05-24T10:00:00"
        }
      ]
    }
  ]
}
```

## Error handling

The backend returns clear HTTP 400 errors for unsupported leagues, invalid teams, and invalid ranges.

Example:

```json
{
  "detail": "invalid team for selected league"
}
```

## Live article source

`GET /source-status`

Returns whether the backend is using only SQLite seed data or live article discovery through NewsAPI.

Example:

```json
{
  "live_news_enabled": true,
  "article_source": "NewsAPI live search + SQLite cache",
  "note": "Add NEWS_API_KEY in backend/.env for live article discovery. Scores and standings should come from a structured sports data API, not news articles."
}
```

To enable live news, create `backend/.env` and set:

```env
NEWS_API_KEY=your_newsapi_key_here
```

The app still falls back to cached/seed data if the API key is missing or the live request fails.
