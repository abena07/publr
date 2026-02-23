# publr

a server that watches a Google Drive folder and automatically publishes new photos to your website and Instagram.

## how it works

```
Google Drive folder
      │
      │ polls every 5 min
      ▼
publr server (FastAPI)
      │
      ├─▶ Cloudflare R2  ──▶  GET /api/photos  ──▶  any website (React / Next.js / Astro / Svelte)
      │
      └─▶ Instagram Graph API  ──▶  published post
```

1. drop a photo into your Google Drive folder
2. publr detects it, resizes it, uploads it to Cloudflare R2
3. posts it to Instagram using the public R2 URL
4. your website fetches `GET /api/photos` and displays it

## setup

see [setup.md](setup.md) for step-by-step instructions.

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
| `POLL_INTERVAL_MINUTES` | how often to check Drive (default 5) |

## run locally

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

- `http://localhost:8000/health` → server status
- `http://localhost:8000/api/photos` → photo list
- `http://localhost:8000/docs` → interactive API explorer
