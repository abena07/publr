# publr

a server that watches a Google Drive folder and automatically publishes new photos to your website and Instagram.

## how it works

```
┌──────────────────────────┐
│       Google Drive       │
│      (your folder)       │
└────────────┬─────────────┘
             │ poll every 5 minutes
             ▼
┌──────────────────────────┐
│      publr server        │
│        (FastAPI)         │
│                          │
│  1. download photo       │
│  2. resize + pad to      │
│     correct aspect ratio │
│  3. upload to Cloudinary │
│  4. post to Instagram    │◄──── retry loop (failed.json)
└────────┬─────────────────┘
         │
         ├─────────────────────────────────────┐
         │                                     │
         ▼                                     ▼
┌─────────────────┐                 ┌──────────────────┐
│   Cloudinary    │                 │    Instagram     │
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

## multi-tenancy architecture

each user connects their own Google Drive and Instagram. credentials are stored per-user in a database, and a separate scheduler job runs for each user.

```
┌─────────────────────────────────────────────────────────┐
│                       database                          │
│                                                         │
│  User ──┬── google_access_token / refresh_token        │
│         ├── instagram_user_id / access_token           │
│         ├── gdrive_folder_id                           │
│         ├── ProcessedFile (gdrive_file_id, processed_at)│
│         └── FailedFile (gdrive_file_id, retry_count)   │
└─────────────────────────────────────────────────────────┘
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
   ┌─────────────────┐     ┌─────────────────┐
   │  per-user job   │     │  per-user job   │
   │  (APScheduler)  │     │  (APScheduler)  │
   │  watches their  │     │  watches their  │
   │  Drive folder   │     │  Drive folder   │
   └─────────────────┘     └─────────────────┘
```

**OAuth flows:**
- Google Drive: OAuth 2.0 — users connect their own Drive via "Connect Google Drive"
- Instagram: Meta OAuth 2.0 — users connect via "Connect Instagram" (requires a Facebook Page linked to an Instagram Business/Creator account)
- Cloudinary: shared account, uploads isolated to `publr/{user_id}/` folder

**dependency order:** db + User model → auth/JWT → (Drive OAuth, Instagram OAuth, per-user state) → per-user scheduler

## env vars

copy `.env.example` to `.env` and fill in your keys:

| key | what it is |
|-----|-----------|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | service account JSON for Drive access |
| `GDRIVE_FOLDER_ID` | ID of the Drive folder to watch |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret |
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
