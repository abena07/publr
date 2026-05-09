from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth.jwt import get_current_user
from app.db.base import AsyncSessionLocal
from app.db.models import User
from app.utils.encryption import encrypt, decrypt

router = APIRouter()


class CloudinaryCredentials(BaseModel):
    cloud_name: str
    api_key: str
    api_secret: str


@router.put("/settings/cloudinary")
async def set_cloudinary_credentials(
    body: CloudinaryCredentials,
    current_user: User = Depends(get_current_user),
):
    async with AsyncSessionLocal() as session:
        user = await session.get(User, current_user.id)
        user.cloudinary_cloud_name = encrypt(body.cloud_name)
        user.cloudinary_api_key = encrypt(body.api_key)
        user.cloudinary_api_secret = encrypt(body.api_secret)
        await session.commit()
    return {"status": "cloudinary credentials saved"}


@router.get("/settings/cloudinary")
async def get_cloudinary_credentials(current_user: User = Depends(get_current_user)):
    has_custom = bool(
        current_user.cloudinary_cloud_name
        and current_user.cloudinary_api_key
        and current_user.cloudinary_api_secret
    )
    return {
        "has_custom_credentials": has_custom,
        "cloud_name": decrypt(current_user.cloudinary_cloud_name) if has_custom else None,
    }


@router.delete("/settings/cloudinary")
async def remove_cloudinary_credentials(current_user: User = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        user = await session.get(User, current_user.id)
        user.cloudinary_cloud_name = None
        user.cloudinary_api_key = None
        user.cloudinary_api_secret = None
        await session.commit()
    return {"status": "cloudinary credentials removed"}
