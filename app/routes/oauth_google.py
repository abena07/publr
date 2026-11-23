"""Sign in with Google: the website-only way into publr (no Instagram needed).

This only signs the user in (openid + email). Connecting Drive is still the
separate flow in oauth_gdrive.py, so the Drive scope stays its own consent.
"""
import os
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select

from app.auth.jwt import create_access_token
from app.auth.oauth_state import create_login_nonce, consume_login_nonce
from app.db.base import AsyncSessionLocal
from app.db.models import User

router = APIRouter()

GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
GOOGLE_LOGIN_REDIRECT_URI = os.environ.get("GOOGLE_LOGIN_REDIRECT_URI", "")

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


@router.get("/auth/google")
async def google_login():
    if not GOOGLE_LOGIN_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="Google sign-in is not configured")
    state = await create_login_nonce()
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_LOGIN_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email",
        "prompt": "select_account",
        "state": state,
    }
    return RedirectResponse(f"{AUTH_URL}?{urlencode(params)}")


@router.get("/auth/google/callback")
async def google_login_callback(code: str = None, error: str = None, state: str = None):
    if error:
        raise HTTPException(status_code=400, detail="Google sign-in was cancelled or denied")
    if not code or not state or not await consume_login_nonce(state):
        raise HTTPException(status_code=400, detail="Invalid or expired state")

    async with httpx.AsyncClient() as client:
        resp = await client.post(TOKEN_URL, data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_LOGIN_REDIRECT_URI,
            "grant_type": "authorization_code",
        })
        tokens = resp.json()
        if "error" in tokens or "access_token" not in tokens:
            raise HTTPException(status_code=400, detail=tokens.get("error_description", "Google sign-in failed"))

        resp = await client.get(USERINFO_URL, headers={"Authorization": f"Bearer {tokens['access_token']}"})
        info = resp.json()

    google_user_id = info.get("sub")
    if not google_user_id:
        raise HTTPException(status_code=400, detail="Google sign-in failed")
    email = info.get("email") if info.get("email_verified") else None

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.google_user_id == google_user_id))
        user = result.scalar_one_or_none()
        if user is None:
            user = User(google_user_id=google_user_id)
            session.add(user)
        if email and user.email != email:
            # email is unique: only set it if no other account already has it
            taken = await session.execute(select(User.id).where(User.email == email, User.id != user.id))
            if taken.scalar_one_or_none() is None:
                user.email = email
        await session.commit()
        await session.refresh(user)

    token = create_access_token(user.id)
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")
    return RedirectResponse(f"{frontend_url}/auth/callback?token={token}")
