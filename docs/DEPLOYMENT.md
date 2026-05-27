# Deployment Notes

## Local MVP

Run backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Run frontend:

```bash
cd frontend
npm install
npm run dev
```

## Backend environment variables

Create `backend/.env` from `.env.example`.

```text
APP_NAME=SportsBrief AI
DATABASE_URL=sqlite:///./sportsbrief.db
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
NEWS_API_KEY=
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
```

## Frontend environment variables

Create `frontend/.env` if the API URL changes.

```text
VITE_API_BASE_URL=http://localhost:8000
```

## Production direction

For a portfolio deployment:

1. Deploy the backend on Render, Railway, Fly.io, or Azure App Service.
2. Replace SQLite with Postgres if multiple users or persistent storage is needed.
3. Deploy the frontend on Vercel, Netlify, or Azure Static Web Apps.
4. Set `VITE_API_BASE_URL` to the deployed backend URL.
5. Set backend `CORS_ORIGINS` to the deployed frontend URL.
6. Keep seed data enabled as a fallback.
7. Add real news integration only after the MVP flow works.
