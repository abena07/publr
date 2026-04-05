import os

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse

from app.auth.jwt import get_current_user
from app.db.base import AsyncSessionLocal
from app.db.models import User

router = APIRouter()

META_APP_ID = os.environ["META_APP_ID"]
META_APP_SECRET = os.environ["META_APP_SECRET"]
META_REDIRECT_URI = os.environ["META_REDIRECT_URI"]
GRAPH_URL = "https://graph.facebook.com/v19.0"


@router.get("/auth/instagram")
async def instagram_auth():
    url = (
        "https://www.facebook.com/v19.0/dialog/oauth"
        f"?client_id={META_APP_ID}"
        f"&redirect_uri={META_REDIRECT_URI}"
        "&scope=instagram_basic,pages_show_list,pages_read_engagement,instagram_content_publish"
        "&response_type=code"
        "&display=page"
        '&extras={"setup":{"channel":"IG_API_ONBOARDING"}}'
    )
    return RedirectResponse(url)


@router.get("/auth/instagram/callback")
async def instagram_callback(code: str):  # TODO: restore Depends(get_current_user) after #24
    async with httpx.AsyncClient() as client:

        # Step 1 — exchange code for short-lived token
        resp = await client.post(f"{GRAPH_URL}/oauth/access_token", data={
            "client_id": META_APP_ID,
            "client_secret": META_APP_SECRET,
            "redirect_uri": META_REDIRECT_URI,
            "code": code,
        })
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

        # Step 3 — get Facebook pages + linked Instagram via user token directly
        resp = await client.get(f"{GRAPH_URL}/me/accounts", params={
            "fields": "id,name,access_token,instagram_business_account",
            "access_token": long_lived_token,
        })
        print(f"DEBUG /me/accounts: {resp.json()}")
        pages = resp.json().get("data", [])

        # fallback: try fetching user's Instagram directly via user token
        if not pages:
            print("DEBUG /me/accounts empty, trying /me?fields=instagram_business_account")
            resp = await client.get(f"{GRAPH_URL}/me", params={
                "fields": "instagram_business_account",
                "access_token": long_lived_token,
            })
            print(f"DEBUG /me direct: {resp.json()}")
            ig = resp.json().get("instagram_business_account")
            if ig:
                instagram_user_id = ig["id"]
                page_access_token = long_lived_token  # use user token directly
            else:
                # TODO: frontend should show a guide modal here walking the user through:
                #   1. Create a Facebook Page
                #   2. Link Instagram via Instagram Settings → Linked Accounts
                #   3. Come back and click Connect Instagram again
                raise HTTPException(status_code=400, detail="You need a Facebook Page linked to your Instagram account to use publr")
        else:
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
                raise HTTPException(status_code=400, detail="No Instagram account found linked to your Facebook Page. Connect it in Instagram Settings → Linked Accounts")

        # Step 5 — check account type
        resp = await client.get(f"{GRAPH_URL}/{instagram_user_id}", params={
            "fields": "account_type",
            "access_token": page_access_token,
        })
        account_type = resp.json().get("account_type")

        if account_type not in ("BUSINESS", "MEDIA_CREATOR"):
            raise HTTPException(status_code=400, detail="Your Instagram must be a Business or Creator account. Go to Instagram Settings → Account type and tools to switch.")

        # Step 6 — TODO: save to user row once #24 provides current_user
        print(f"instagram_user_id: {instagram_user_id}")
        print(f"page_access_token: {page_access_token[:20]}...")

        return {"instagram_user_id": instagram_user_id, "status": "connected"}
