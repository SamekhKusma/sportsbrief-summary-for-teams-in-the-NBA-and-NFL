# SportsBrief

SportsBrief is a full-stack sports news summarizer MVP for NBA and NFL fans. Users choose a league, select a team, pick a time range, and generate a concise AI-style brief with topic grouping, sentiment labels, importance scores, and source links.

The project is designed as a student portfolio MVP. It works with mock seed data by default, so no external API key is required.

## Features

- League selector for NBA and NFL
- Team selector with all NBA and NFL teams
- Time range selector for last 24 hours, last 3 days, and last 7 days
- Filtered news feed by league and team
- Duplicate article removal
- Weakly related article filtering
- Topic grouping
  - Injuries
  - Trades / roster moves
  - Game results
  - Upcoming games
  - Coaching / front office
  - Player performance
  - Rumors
  - Other
- Team summary under 150 words
- Topic summaries under 75 words
- Sentiment labels: Positive, Negative, Neutral, Mixed
- Importance score from 1 to 5
- Source links for every topic
- SQLite caching through SQLAlchemy
- Mock NBA and NFL seed data
- Basic backend tests
- Clean React frontend with responsive cards

## Tech stack

### Frontend

- React
- Vite
- Tailwind CSS

### Backend

- Python
- FastAPI
- SQLite
- SQLAlchemy
- Pydantic

## Project structure

```text
sportsbrief-ai/
  backend/
    app/
      main.py
      config.py
      database.py
      models.py
      schemas.py
      seed.py
      services/
        news_service.py
        summarizer.py
      data/
        seed_articles.json
        teams.json
    tests/
      test_api.py
    requirements.txt
  frontend/
    src/
      App.jsx
      api.js
      main.jsx
      index.css
    package.json
    vite.config.js
    tailwind.config.js
    postcss.config.js
  docs/
    API.md
    DATABASE_SCHEMA.md
    DEPLOYMENT.md
    LLM_PROMPT.md
    SCREENSHOTS.md
  .env.example
  README.md
```

## Run the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at:

```text
http://localhost:8000
```

Interactive API docs:

```text
http://localhost:8000/docs
```

## Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

```text
http://localhost:5173
```

## Run backend tests

```bash
cd backend
pytest
```

## MVP workflow

1. Open the frontend.
2. Choose NBA or NFL.
3. Select a team.
4. Select a time range.
5. Click Generate Brief.
6. Review the team summary, topic cards, and source links.

## Optional real news integration

The MVP is built to work with seed data first. Real news API integration should be added behind environment variables. The recommended path is:

1. Keep seed data as the default fallback.
2. Add a `NEWS_API_KEY` to `.env`.
3. Add a provider in `backend/app/services/news_service.py`.
4. Normalize external results into the same article schema.
5. Cache normalized articles in SQLite.

Do not scrape full copyrighted articles. Use only metadata such as title, description, snippet, source, URL, and publish date.

## AI behavior

The backend includes a deterministic summarizer fallback so the MVP works without an LLM key. It returns strict JSON in the same shape expected from an LLM. The LLM prompt and output contract are documented in `docs/LLM_PROMPT.md`.

## Example summary response

```json
{
  "team": "Los Angeles Lakers",
  "league": "NBA",
  "summary": "Los Angeles Lakers news is centered on injury management and roster planning. The biggest items are grouped below with source links for verification.",
  "topics": [
    {
      "category": "Injuries",
      "headline": "Lakers monitor guard injury status",
      "summary": "The Lakers are monitoring a guard's ankle soreness before the next game. Availability is not confirmed in the provided sources.",
      "importance": 4,
      "sentiment": "Negative",
      "sources": [
        {
          "title": "Lakers guard listed as questionable with ankle soreness",
          "url": "https://example.com/lakers-injury",
          "source_name": "Mock Sports Wire",
          "published_at": "2026-05-24T10:00:00"
        }
      ]
    }
  ]
}
```


## Live news setup

The first version works with mock seed data only. To make the app pull recent articles, create `backend/.env` and add a NewsAPI key:

```env
NEWS_API_KEY=your_newsapi_key_here
```

Then restart the backend. The app will use NewsAPI live search first and cache matching articles in SQLite. If no key is provided, the app clearly shows that it is using seed data only.

Side note: Live news APIs are for articles, not official scores or playoff series state. For exact scores, standings, schedules, and series records, add a structured sports data API such as SportsDataIO, Sportradar, or an official league feed later.
