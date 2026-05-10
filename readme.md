# publr

a server that watches a Google Drive folder and automatically publishes new photos to your website and Instagram.

want to use the hosted version? join the waitlist at [publr.bennett-eghan.com/join](https://publr.bennett-eghan.com/join). you can bring your own Cloudinary account or use the default one.

want to add publr to your website? see [publr.bennett-eghan.com/docs](https://publr.bennett-eghan.com/docs)

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
│  4. post to Instagram    │◄──── retry loop (db)
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

## self-hosting

### prerequisites

**Instagram:** you need a Facebook Page linked to an Instagram Business or Creator account. personal Instagram accounts cannot publish via the API.

**Meta app:** create an app at developers.facebook.com, add the Instagram product, and set the OAuth redirect URI to `{your_domain}/auth/instagram/callback`.

**Google app:** create an OAuth 2.0 client at console.cloud.google.com with the Google Drive API enabled. set the redirect URI to `{your_domain}/auth/gdrive/callback`.

**Cloudinary:** create a free account at cloudinary.com. photos are uploaded under a `publr/{user_id}/` folder so each user's images stay separate.

### env vars

copy `.env.example` to `.env` and fill in your keys:

| key | what it is |
|-----|-----------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing key (any long random string) |
| `FIELD_ENCRYPTION_KEY` | Fernet key — generate with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| `META_APP_ID` | Meta app ID |
| `META_APP_SECRET` | Meta app secret |
| `META_REDIRECT_URI` | full URL to `/auth/instagram/callback` |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret |
| `GOOGLE_REDIRECT_URI` | full URL to `/auth/gdrive/callback` |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret |
| `FRONTEND_URL` | URL of your frontend (for CORS) |
| `PORT` | server port (default 8000) |
| `POLL_INTERVAL_MINUTES` | how often to check Drive (default 5) |
| `PUBLIC_CONTACT_EMAIL` | optional — shown on `/privacy` |

### setup

```bash
git clone git@github.com:abena07/publr.git
cd publr

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# fill in your keys in .env

alembic upgrade head
```

### run locally

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

- `http://localhost:8000/docs` → interactive API explorer
- `http://localhost:8000/api/photos` → photo list
- `http://localhost:8000/privacy` → privacy policy

## contributing

prs welcome. open an issue and attach a pr if you can, or we can discuss and take it from there.
