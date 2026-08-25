# Usage Guide

## For visitors

1. Open a creator's page, e.g. `https://yourdomain.com/demo`
2. Tap any link — you're redirected to the target site; the creator's click counter goes up.

## For creators

### Create your page

1. Go to `/app` → **Sign up** (email, username, password).
2. You're logged in automatically with a JWT (valid 24h).

### Add links

1. **My Links** → fill Title + URL, pick an icon, set the order.
2. Click **+ Add link** — it's live instantly on `/yourname`.
3. Use 👁️/🙈 to toggle a link on/off without deleting it. 🗑️ deletes.
4. The click count next to each link shows lifetime taps.

### Customize your page

1. **Page Settings** → display name, bio, avatar URL, theme.
2. Themes: midnight, sunset, forest, ocean, mono. Saved instantly.

### Track performance

1. **Analytics** → total clicks, total links, clicks today.
2. A 14-day bar chart shows the daily trend.
3. **Top links** lists your best performers with lifetime clicks.

### QR codes

Every active link has a QR endpoint: `/qr/{link_id}`. Print it on business cards, menus, or packaging. (A UI button for this is on the roadmap; the endpoint is live.)

## Roles & permissions

| Action | Anonymous | Owner |
|---|---|---|
| View public page | ✅ | ✅ |
| Click redirect | ✅ | ✅ |
| Scan QR | ✅ | ✅ |
| Register/login | ✅ | ✅ |
| Manage links | ❌ | ✅ |
| View analytics | ❌ | ✅ |
| Edit page settings | ❌ | ✅ |
| Edit/delete others' links | ❌ | ❌ (404) |

## Troubleshooting

- **"Email or username already registered"** — usernames are globally unique (that's your public URL).
- **Login rate limited** — 10 attempts/min per IP. Wait a minute.
- **QR shows 404** — the link is inactive or deleted.
- **Demo login fails** — run `python -m scripts.seed` first.
