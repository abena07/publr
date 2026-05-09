import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from sqlalchemy import select

import app.db.models  # noqa: F401 — registers models with Base
from app.scheduler import scheduler
from app.watchers.gdrive import start_watcher
from app.routes.photos import router as photos_router
from app.routes.oauth_instagram import router as instagram_router
from app.routes.oauth_gdrive import router as gdrive_router
from app.routes.legal import router as legal_router
from app.routes.cloudinary_settings import router as cloudinary_router
from app.routes.me import router as me_router
from app.db.base import engine, Base, AsyncSessionLocal
from app.db.models import User

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.google_access_token.isnot(None))
        )
        users = result.scalars().all()

    for user in users:
        start_watcher(user.id)

    scheduler.start()
    yield


app = FastAPI(title="publr", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(photos_router)
app.include_router(instagram_router)
app.include_router(gdrive_router)
app.include_router(legal_router)
app.include_router(cloudinary_router)
app.include_router(me_router)
