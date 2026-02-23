# publr

a server that watches a Google Drive folder and automatically publishes new photos to your website and Instagram.

## how it works

```
┌──────────────────────────┐
│       Google Drive       │
│      (your folder)       │
└────────────┬─────────────┘
             │ push notification on upload
             │ (falls back to 5-min poll locally)
             ▼
┌──────────────────────────┐
│      publr server        │
│        (FastAPI)         │
│                          │
│  1. download photo       │
│  2. resize via Pillow    │
│  3. upload to R2         │
│  4. post to Instagram    │
└────────┬─────────────────┘
         │
         ├─────────────────────────────────────┐
         │                                     │
         ▼                                     ▼
┌─────────────────┐                 ┌──────────────────┐
│  Cloudflare R2  │                 │    Instagram     │
│   (public CDN)  │                 │   Graph API      │
└────────┬────────┘                 └──────────────────┘
         │
         │ GET /api/photos
         ▼
┌─────────────────────────────────────────────┐
│              your website                   │
│   React  /  Next.js  /  Astro  /  Svelte    │
└─────────────────────────────────────────────┘
```

> **note on triggering:** when deployed (Railway/Fly.io), publr registers a webhook with the Google Drive API so it fires instantly on upload — no polling needed. locally it falls back to polling every 5 minutes since Drive webhooks require a public HTTPS URL.

## env vars

copy `.env.example` to `.env` and fill in your keys:

| key | what it is |
|-----|-----------|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | service account JSON for Drive access |
| `GDRIVE_FOLDER_ID` | ID of the Drive folder to watch |
| `R2_ACCOUNT_ID` | Cloudflare account ID |
| `R2_ACCESS_KEY_ID` | R2 API token key |
| `R2_SECRET_ACCESS_KEY` | R2 API token secret |
| `R2_BUCKET_NAME` | R2 bucket name |
| `R2_PUBLIC_URL` | public base URL for your bucket |
| `INSTAGRAM_USER_ID` | Instagram business/creator account ID |
| `INSTAGRAM_ACCESS_TOKEN` | long-lived access token (60-day expiry) |
| `PORT` | server port (default 8000) |
| `POLL_INTERVAL_MINUTES` | fallback poll interval for local dev (default 5) |

## run locally

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

- `http://localhost:8000/health` → server status
- `http://localhost:8000/api/photos` → photo list
- `http://localhost:8000/docs` → interactive API explorer
