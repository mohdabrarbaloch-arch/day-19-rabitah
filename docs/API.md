# API Reference

Base URL: `http://localhost:8000` (or your deployed domain).  
All protected endpoints require header: `Authorization: Bearer <token>`.

## Health

### GET /api/health
```json
{ "status": "ok", "app": "Rabitah API", "version": "1.0.0" }
```

## Auth

### POST /api/auth/register
Body:
```json
{ "email": "you@example.com", "username": "yourname", "password": "secret123" }
```
- `username`: 3–30 chars, lowercase letters/digits/underscore.
- `password`: ≥ 8 chars, must contain a digit.
- Returns `{ "access_token": "...", "token_type": "bearer" }` (201).
- `409` if email or username taken. `422` on validation failure. Rate limit: 5/min.

### POST /api/auth/login
Body:
```json
{ "email": "you@example.com", "password": "secret123" }
```
Returns `{ "access_token": "...", "token_type": "bearer" }`. `401` on bad credentials. Rate limit: 10/min.

### GET /api/auth/me
Returns the current profile:
```json
{ "id": 1, "username": "yourname", "display_name": "Your Name", "bio": "", "avatar_url": "", "theme": "midnight" }
```

### PATCH /api/auth/me
Body (any subset):
```json
{ "display_name": "New Name", "bio": "hi", "avatar_url": "https://...", "theme": "sunset" }
```
`theme` must be one of: `midnight`, `sunset`, `forest`, `ocean`, `mono`.

## Links

### GET /api/links
List the authenticated user's links (ordered by sort_order, then id).

### POST /api/links
Body:
```json
{ "title": "My GitHub", "url": "https://github.com/me", "icon": "github", "sort_order": 0, "is_active": true }
```
- `url` must start with `http://` or `https://` (422 otherwise).

### PATCH /api/links/{id}
Body (any subset): `title`, `url`, `icon`, `sort_order`, `is_active`. Returns the updated link.

### DELETE /api/links/{id}
Returns `204 No Content`. Foreign links → `404`.

## Public

### GET /{username}
Returns the public page payload:
```json
{
  "username": "yourname",
  "display_name": "Your Name",
  "bio": "...",
  "avatar_url": "",
  "theme": "midnight",
  "links": [ { "id": 1, "title": "My GitHub", "url": "https://...", "icon": "github" } ]
}
```
Also available as JSON-only at `GET /api/page/{username}`. `404` if the user doesn't exist or is inactive.

### GET /go/{link_id}
302-redirects to the link's URL and increments its click count. `404` for missing/inactive links.

### GET /qr/{link_id}
Returns a PNG QR code encoding the link URL. `404` for missing/inactive links.

## Analytics

### GET /api/analytics?days=14
Requires auth. Returns:
```json
{
  "total_clicks": 12,
  "total_links": 3,
  "daily": [ { "date": "2026-08-12", "count": 2 }, ... ],
  "top_links": [ { "id": 1, "title": "...", "url": "...", "icon": "github", "sort_order": 0, "is_active": true, "click_count": 12, "created_at": "..." } ]
}
```
`days` clamped to 1–90.

## Error format

All errors return JSON: `{ "detail": "human readable message" }` with appropriate status codes (401, 404, 409, 422, 429).
