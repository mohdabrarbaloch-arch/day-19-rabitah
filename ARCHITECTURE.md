# Rabitah — Architecture

## Overview

Rabitah is a link-in-bio / micro-page builder. Creators register, add links, customize their page theme, and share one URL. Every click on every link is counted and recorded so creators can see which links actually perform.

## System diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                          Browser                                 │
│   Landing (/) · Dashboard (/app) · Public page (/username)       │
└─────────────────────────────────────────┬────────────────────────┘
                                          │ HTTP/JSON
┌─────────────────────────────────────────▼────────────────────────┐
│                        FastAPI app                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐     │
│  │  auth    │ │  links   │ │  page    │ │  analytics       │     │
│  │ /register│ │ CRUD +   │ │ /{user}  │ │ totals, daily,   │     │
│  │ /login   │ │ ownership│ │ /go/{id} │ │ top links        │     │
│  │ /me      │ │ check    │ │ /qr/{id} │ │                  │     │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────────┬─────────┘     │
│       │            │            │                │               │
│  JWT + bcrypt  SQLAlchemy 2.0 (session)           │               │
└────────────┬──────────────┬──────────────┬──────────────┬────────┘
             │              │              │              │
┌────────────▼──────────────▼──────────────▼──────────────▼────────┐
│                     Database (SQLite/Postgres)                   │
│   users ──< links ──< click_events                                │
└──────────────────────────────────────────────────────────────────┘
```

## Data model

```
users
  id            PK
  email         unique, indexed
  username      unique, indexed (the public page slug)
  hashed_password  bcrypt
  display_name, bio, avatar_url, theme
  is_active     soft-disable
  created_at

links
  id            PK
  user_id       FK → users (CASCADE)
  title, url, icon, sort_order, is_active
  click_count   denormalized counter (fast reads)

click_events
  id            PK
  link_id       FK → links (CASCADE)
  user_id       FK → users (CASCADE)
  referrer, user_agent
  clicked_at    indexed
```

`click_count` on `links` is denormalized so the public dashboard and top-links list never need to aggregate events. Raw events power the daily chart.

## Key flows

### 1. Click redirect (the hot path)

```
Visitor → GET /go/{link_id}
  → link found & active? no  → 404
  → link.click_count += 1
  → INSERT click_event (referrer, user_agent)
  → COMMIT
  → 302 Redirect to link.url
```

### 2. Public page

```
GET /{username}
  → user by username (lowercased), is_active?
  → collect links where is_active
  → return theme + links as JSON (the /username route serves JSON;
    the SPA-rendered page fetches /api/page/{username} for the same payload)
```

### 3. Analytics

```
GET /api/analytics?days=14 (JWT required)
  → links of user, ordered by click_count desc (top 5)
  → click_events since (today - days + 1), grouped by DATE(clicked_at)
  → build a zero-filled daily series so charts render cleanly
```

## Security

- **Passwords** — bcrypt (12 rounds) via passlib; never stored in plaintext.
- **Tokens** — JWT HS256, 24h expiry, secret only from env (`SECRET_KEY`).
- **Rate limiting** — SlowAPI: 10 logins/min, 5 registrations/min per IP.
- **CORS** — allow-list from env (`CORS_ORIGINS`), default `*` for dev.
- **Input validation** — Pydantic: URL scheme whitelist (`http/https`), username charset, password strength.
- **Ownership** — every link mutation checks `link.user_id == current_user.id`; foreign access returns 404 (no existence leak).
- **No secrets in code** — everything configurable via `.env`.

## Scaling notes

- **SQLite → Postgres** — ORM layer is provider-agnostic; swap `DATABASE_URL` in `.env`/compose. Postgres 16 docker-compose included.
- **Click volume** — if redirect traffic grows, move the counter increment to a Redis INCR and flush `click_events` in batches; the denormalized `click_count` keeps reads cheap meanwhile.
- **Read-heavy public pages** — `/{username}` is a single indexed lookup (username unique index); pages are static-ish per user and could be cached or pre-rendered at CDN edge.
- **Vercel serverless** — `api/index.py` exposes the ASGI app; static assets served by `@vercel/static`. SQLite works on `/tmp` per instance for demos; use managed Postgres for production.
- **Future** — add `page_views` table for profile-level stats, custom slugs per link, and referrer breakdowns (available in `click_events.referrer` already).

## Environment variables

See [`.env.example`](../.env.example). All settings load at startup via pydantic-settings; `get_settings()` is cached so tests can override via env before import.
