from contextlib import asynccontextmanager

from fastapi import FastAPI
from dotenv import load_dotenv

import app.db.models  # noqa: F401 — registers models with Base
from app.watchers.gdrive import start_watcher
from app.routes.photos import router as photos_router
from app.routes.oauth_instagram import router as instagram_router
from app.routes.oauth_gdrive import router as gdrive_router
from app.routes.legal import router as legal_router
from app.db.base import engine, Base

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    start_watcher()
    yield


app = FastAPI(title="publr", lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(photos_router)
app.include_router(instagram_router)
app.include_router(gdrive_router)
app.include_router(legal_router)


