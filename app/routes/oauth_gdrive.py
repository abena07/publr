import os
import re
import time
import uuid

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from app.scheduler import scheduler
from app.auth.jwt import get_current_user, decode_token
from app.auth.oauth_state import create_state, consume_state
from app.db.base import AsyncSessionLocal
from app.db.models import User
from app.watchers.gdrive import start_watcher

router = APIRouter()

GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
GOOGLE_REDIRECT_URI = os.environ["GOOGLE_REDIRECT_URI"]

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPES = "https://www.googleapis.com/auth/drive.readonly"


@router.get("/auth/gdrive/start")
async def gdrive_auth_start(token: str):
    """Browser-friendly GDrive OAuth — accepts JWT as query param for redirect flows."""
    user_id_str = decode_token(token)
    async with AsyncSessionLocal() as session:
        user = await session.get(User, uuid.UUID(user_id_str))
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
    state = await create_state(uuid.UUID(user_id_str))
    url = (
        f"{AUTH_URL}"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope={SCOPES}"
        f"&access_type=offline"
        f"&prompt=consent"
        f"&state={state}"
    )
    return RedirectResponse(url)


@router.get("/auth/gdrive")
async def gdrive_auth(current_user: User = Depends(get_current_user)):
    state = await create_state(current_user.id)
    url = (
        f"{AUTH_URL}"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope={SCOPES}"
        f"&access_type=offline"
        f"&prompt=consent"
        f"&state={state}"
    )
    return RedirectResponse(url)


@router.get("/auth/gdrive/callback")
async def gdrive_callback(code: str, state: str):
    user_id = await consume_state(state)
    if user_id is None:
        raise HTTPException(status_code=400, detail="Invalid or expired state")

    async with httpx.AsyncClient() as client:
        resp = await client.post(TOKEN_URL, data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        })
        data = resp.json()

    if "error" in data:
        raise HTTPException(status_code=400, detail=data.get("error_description", data["error"]))

    async with AsyncSessionLocal() as session:
        user = await session.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        user.google_access_token = data["access_token"]
        if data.get("refresh_token"):
            user.google_refresh_token = data["refresh_token"]
        user.google_token_expires_at = int(time.time()) + data.get("expires_in", 3600)
        user.gdrive_connected = True
        await session.commit()

    # Completing OAuth is enough to be connected — don't depend on the frontend
    # to POST /settings/gdrive/connect afterwards. Resume a paused watcher if one
    # already exists (e.g. after a prior disconnect), otherwise start a new one.
    job_id = f"gdrive_watcher_{user_id}"
    if scheduler.get_job(job_id):
        scheduler.resume_job(job_id)
    else:
        start_watcher(user_id)

    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")
    return RedirectResponse(f"{frontend_url}/dashboard?gdrive=connected")


class GDriveSettings(BaseModel):
    folder_id: str


@router.put("/settings/gdrive")
async def set_gdrive_folder(body: GDriveSettings, current_user: User = Depends(get_current_user)):
    folder_id = body.folder_id.strip()
    match = re.search(r"/folders/([a-zA-Z0-9_-]+)", folder_id)
    if match:
        folder_id = match.group(1)
    async with AsyncSessionLocal() as session:
        user = await session.get(User, current_user.id)
        user.gdrive_folder_id = folder_id
        await session.commit()
    return {"gdrive_folder_id": folder_id}


@router.post("/settings/gdrive/connect")
async def connect_drive(current_user: User = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        user = await session.get(User, current_user.id)
        user.gdrive_connected = True
        await session.commit()
    job_id = f"gdrive_watcher_{current_user.id}"
    if scheduler.get_job(job_id):
        scheduler.resume_job(job_id)
    else:
        start_watcher(current_user.id)
    return {"status": "connected"}


@router.delete("/settings/gdrive/disconnect")
async def disconnect_drive(current_user: User = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        user = await session.get(User, current_user.id)
        user.gdrive_connected = False
        user.google_access_token = None
        user.google_refresh_token = None
        user.google_token_expires_at = None
        user.gdrive_folder_id = None
        await session.commit()
    scheduler.remove_job(f"gdrive_watcher_{current_user.id}")
    return {"status": "disconnected"}
