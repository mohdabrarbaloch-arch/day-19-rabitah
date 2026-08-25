# Setup Guide

## Prerequisites

- Python 3.11+
- Node.js 20+ (only if you use the Vercel CLI)
- Docker + Docker Compose (optional, for Postgres)

## 1. Local development (SQLite)

```bash
git clone https://github.com/mohdabrarbaloch-arch/day-19-rabitah.git
cd day-19-rabitah

python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env            # defaults are fine for local dev

uvicorn app.main:app --reload
```

- App: http://localhost:8000
- API docs (Swagger): http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

## 2. Seed demo data (optional)

```bash
python -m scripts.seed
```

Creates `demo@rabitah.pk / demo12345` with 5 links and ~60 days of fake click history so the analytics chart isn't empty. Public page: http://localhost:8000/demo

## 3. Docker + PostgreSQL

```bash
docker-compose up --build
```

- App: http://localhost:8000
- Postgres: `localhost:5432`, db `rabitah`, user `rabitah`, password `rabitah`
- `DATABASE_URL=postgresql+psycopg2://rabitah:rabitah@db:5432/rabitah`

## 4. Running tests

```bash
pytest -q
```

The test suite uses an isolated temporary SQLite DB and resets tables before every test — no setup needed.

## 5. Linting & formatting

```bash
ruff check .      # lint
ruff format .     # format
```

## 6. Deploy to Vercel

The repo is Vercel-ready (`vercel.json` + `api/index.py` + `@vercel/python` + `@vercel/static`).

```bash
npm i -g vercel
vercel login              # one-time, browser flow
vercel --prod --yes --token $VERCEL_TOKEN
```

Environment variables to set in Vercel dashboard:

| Key | Value |
|---|---|
| `SECRET_KEY` | long random string (`python -c "import secrets; print(secrets.token_urlsafe(64))"`) |
| `DATABASE_URL` | managed Postgres URL (Neon/Supabase/Railway) — SQLite on `/tmp` works for demos but resets per instance |
| `CORS_ORIGINS` | your domains, comma-separated |
