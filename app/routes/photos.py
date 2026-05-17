import os
import uuid

import cloudinary
import cloudinary.api
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app.auth.jwt import get_current_user
from app.db.base import AsyncSessionLocal
from app.db.models import User
from app.publishers.cloudinary import make_display_url
from app.utils.encryption import decrypt

router = APIRouter()


def _fetch_photos(user: User) -> list[str]:
    has_custom = bool(
        user.cloudinary_cloud_name
        and user.cloudinary_api_key
        and user.cloudinary_api_secret
    )
    if has_custom:
        cloudinary.config(
            cloud_name=decrypt(user.cloudinary_cloud_name),
            api_key=decrypt(user.cloudinary_api_key),
            api_secret=decrypt(user.cloudinary_api_secret),
        )
        prefix = "publr"
    else:
        cloudinary.config(
            cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
            api_key=os.environ["CLOUDINARY_API_KEY"],
            api_secret=os.environ["CLOUDINARY_API_SECRET"],
        )
        prefix = f"publr/{user.id}"

    result = cloudinary.api.resources(type="upload", prefix=prefix, max_results=100)
    resources = sorted(result["resources"], key=lambda r: r["created_at"], reverse=True)
    return [make_display_url(r["secure_url"]) for r in resources]


@router.get("/api/photos/{user_id}")
async def get_photos_public(user_id: uuid.UUID):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    return {"photos": _fetch_photos(user)}


@router.get("/api/photos")
async def get_photos(current_user: User = Depends(get_current_user)):
    return {"photos": _fetch_photos(current_user)}
