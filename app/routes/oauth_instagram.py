import os

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy import select

from app.auth.jwt import create_access_token
from app.auth.oauth_state import create_login_nonce, consume_login_nonce
from app.db.base import AsyncSessionLocal
from app.db.models import User

router = APIRouter()

META_APP_ID = os.environ["META_APP_ID"]
META_APP_SECRET = os.environ["META_APP_SECRET"]
META_REDIRECT_URI = os.environ["META_REDIRECT_URI"]
GRAPH_URL = "https://graph.facebook.com/v19.0"


@router.get("/auth/instagram")
async def instagram_auth():
    state = await create_login_nonce()
    url = (
        "https://www.facebook.com/v19.0/dialog/oauth"
        f"?client_id={META_APP_ID}"
        f"&redirect_uri={META_REDIRECT_URI}"
        "&scope=instagram_basic,pages_show_list,pages_read_engagement,instagram_content_publish"
        "&response_type=code"
        "&display=page"
        f"&state={state}"
        '&extras={"setup":{"channel":"IG_API_ONBOARDING"}}'
    )
    return RedirectResponse(url)


@router.get("/auth/instagram/callback")
async def instagram_callback(code: str = None, error: str = None, state: str = None):
    print(f"DEBUG callback: code={code}, error={error}, state={state}")
    if error:
        raise HTTPException(status_code=400, detail="Instagram login was cancelled or denied")
    if not state or not await consume_login_nonce(state):
        raise HTTPException(status_code=400, detail="Invalid or expired state")

    async with httpx.AsyncClient() as client:

        # Step 1 — exchange code for short-lived token
        resp = await client.post(f"{GRAPH_URL}/oauth/access_token", data={
            "client_id": META_APP_ID,
            "client_secret": META_APP_SECRET,
            "redirect_uri": META_REDIRECT_URI,
            "code": code,
        })
        print(f"DEBUG short-lived token exchange: {resp.json()}")
        short_lived_token = resp.json()["access_token"]

        # Step 2 — exchange short-lived for long-lived token
        resp = await client.get(f"{GRAPH_URL}/oauth/access_token", params={
            "grant_type": "fb_exchange_token",
            "client_id": META_APP_ID,
            "client_secret": META_APP_SECRET,
            "fb_exchange_token": short_lived_token,
        })
        print(f"DEBUG long-lived token exchange: {resp.json()}")
        long_lived_token = resp.json()["access_token"]

        # Debug — check what permissions were actually granted
        resp = await client.get(f"{GRAPH_URL}/me/permissions", params={"access_token": long_lived_token})
        print(f"DEBUG /me/permissions: {resp.json()}")

        # Step 3 — get Facebook pages + linked Instagram via user token directly
        resp = await client.get(f"{GRAPH_URL}/me/accounts", params={
            "fields": "id,name,access_token,instagram_business_account",
            "access_token": long_lived_token,
        })
        print(f"DEBUG /me/accounts: {resp.json()}")
        pages = resp.json().get("data", [])

        if not pages:
            raise HTTPException(
                status_code=400,
                detail=(
                    "No Facebook Pages found for this account. "
                    "Create/select a Page and link your Instagram Professional account."
                ),
            )

        # Step 4 — find Instagram account linked to a page
        instagram_user_id = None
        page_access_token = None

        for page in pages:
            ig = page.get("instagram_business_account")
            if ig:
                instagram_user_id = ig["id"]
                page_access_token = page["access_token"]
                break

        if not instagram_user_id:
            raise HTTPException(
                status_code=400,
                detail=(
                    "No Instagram Professional account linked to your selected Facebook Page. "
                    "Connect it and retry."
                ),
            )

        # Step 5 — check publish eligibility.
        # Graph API account_type is not consistently available for this node;
        # probe /media and treat code 10 as not publish-eligible.
        probe = await client.post(
            f"{GRAPH_URL}/{instagram_user_id}/media",
            data={"access_token": page_access_token},
        )
        probe_data = probe.json()
        print(f"DEBUG /{instagram_user_id}/media probe: {probe_data}")
        probe_error = probe_data.get("error", {})

        if probe_error.get("code") == 10:
            raise HTTPException(
                status_code=400,
                detail=(
                    "This Instagram account is not currently publish-eligible in this app context. "
                    "Use a Business account or update Meta app/account permissions."
                ),
            )

    # Step 6 — find or create user, issue JWT
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.instagram_user_id == instagram_user_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            user = User(
                instagram_user_id=instagram_user_id,
                instagram_access_token=page_access_token,
            )
            session.add(user)
        else:
            user.instagram_access_token = page_access_token

        await session.commit()
        await session.refresh(user)

    token = create_access_token(user.id)
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")
    return RedirectResponse(f"{frontend_url}/auth/callback?token={token}")
