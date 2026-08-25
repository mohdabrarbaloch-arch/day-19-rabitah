# Rabitah (رابطہ) — Your links, one smart page

**Day 19 of the 30-Day Build Challenge** · A smart link-in-bio & micro-page builder for creators.

> Creators in Pakistan juggle a link in every bio — Instagram, TikTok, Fiverr, YouTube. Rabitah gathers them all on one beautiful page, tracks every click, and gives you a QR code your followers can scan.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00)
![JWT](https://img.shields.io/badge/Auth-JWT%20%2B%20bcrypt-000000)
![Tests](https://img.shields.io/badge/tests-29%20passed-2ea44f)
![Lint](https://img.shields.io/badge/ruff-clean-2ea44f)
![License](https://img.shields.io/badge/License-MIT-blue)

---

## The problem

Every creator has the same mess: five platforms, five different link-in-bio pages, zero idea which one actually gets clicked. Businesses on Instagram want one clean page that sends followers to their WhatsApp, their Fiverr gig, their YouTube channel — without looking like a link dump.

Rabitah gives you **one beautiful page** (`/yourname`), **click tracking** so you know what works, **QR codes** for offline sharing, and **themes** so it looks like you, not a template.

## Features

- 🔗 **Link manager** — add, reorder, toggle, delete links with icons (GitHub, YouTube, TikTok, WhatsApp, Fiverr, calendar, email…)
- 📊 **Click analytics** — 14-day daily click chart + top performing links
- 🎨 **5 themes** — midnight, sunset, forest, ocean, mono — switch in one tap
- 📱 **QR codes** — every link gets a scannable PNG for cards, stalls, and packaging
- ⚡ **Smart redirects** — `/go/{id}` counts the click and bounces visitors in one hop
- 🔐 **Secure** — JWT auth (24h), bcrypt hashing, rate-limited auth, validated URLs, role-scoped queries
- 📱 **Mobile-first SPA** — zero build step, works on any phone

## Screenshots

Coming soon — the repo is fully runnable locally (`uvicorn app.main:app --reload` → visit `/app` to register and `/demo` for the seeded demo page), so you can grab your own captures in two minutes.

## Tech stack

| Layer | Technology |
|---|---|
| Backend | FastAPI 0.115 · Python 3.11 · SQLAlchemy 2.0 · Pydantic v2 |
| Auth | JWT (HS256, 24h) · bcrypt (12 rounds) · SlowAPI rate limits |
| Database | SQLite (dev, WAL) · PostgreSQL 16 (docker-compose) |
| Frontend | Vanilla JS · mobile-first dark SPA · no build step |
| QR | `qrcode` + Pillow |
| Infra | Docker · docker-compose · Vercel-ready serverless |

## Quick start (local)

```bash
git clone https://github.com/mohdabrarbaloch-arch/day-19-rabitah.git
cd day-19-rabitah

# 1. Python 3.11+ with venv
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env

# 3. Run
uvicorn app.main:app --reload
# API docs at http://localhost:8000/docs
```

Seed a demo user (optional):

```bash
python -m scripts.seed
# demo@rabitah.pk / demo12345 — public page at /demo
```

## Docker (PostgreSQL)

```bash
docker-compose up --build
# app on http://localhost:8000, Postgres on 5432
```

## Testing & linting

```bash
pytest -q            # 29 tests
ruff check .         # lint
ruff format .        # format
```

## API overview

| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/register` | Create account → JWT |
| POST | `/api/auth/login` | Log in → JWT |
| GET | `/api/auth/me` | Current profile |
| PATCH | `/api/auth/me` | Update profile/theme |
| GET | `/api/links` | List my links |
| POST | `/api/links` | Create link |
| PATCH | `/api/links/{id}` | Update link |
| DELETE | `/api/links/{id}` | Delete link |
| GET | `/{username}` | Public page (HTML/JSON) |
| GET | `/go/{id}` | Click redirect + counter |
| GET | `/qr/{id}` | QR code PNG |
| GET | `/api/analytics?days=14` | Click stats |

Full reference in [`docs/API.md`](docs/API.md).

## Deployment (Vercel)

The repo ships Vercel-ready: `vercel.json` + `api/index.py`. Deploy with:

```bash
vercel --prod --yes --token $VERCEL_TOKEN
```

Set the env vars from `.env.example` in Vercel's dashboard. For a persistent database, point `DATABASE_URL` at a managed Postgres (Neon/Supabase/Railway).

## Project structure

```
app/
  core/          config, database, security, deps
  routers/       auth, links, page (public), analytics
  services/      QR code generation
  models.py      User, Link, ClickEvent
  schemas.py     Pydantic request/response models
  main.py        FastAPI app
static/          landing page, dashboard SPA, public page
tests/           29 unit + API tests
docs/            SETUP, USAGE, API reference
api/index.py     Vercel serverless entry
scripts/seed.py  demo data seeder
```

## Roadmap

- [ ] Custom slugs (e.g. `yourname/shop`)
- [ ] Link click graphs by referrer (Instagram vs TikTok vs direct)
- [ ] Bio link "trees" for multi-page profiles
- [ ] Team/business accounts with multiple admins

## License

[MIT](LICENSE) — built by Mohd Abrar Baloch, Day 19 of the 30-day build challenge.
