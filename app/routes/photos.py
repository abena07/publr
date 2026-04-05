import os

import cloudinary
import cloudinary.api
from fastapi import APIRouter, Depends

from app.auth.jwt import get_current_user
from app.db.models import User

cloudinary.config(
    cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
    api_key=os.environ["CLOUDINARY_API_KEY"],
    api_secret=os.environ["CLOUDINARY_API_SECRET"],
)

router = APIRouter()

@router.get("/api/photos")
async def get_photos(current_user: User = Depends(get_current_user)):
    result = cloudinary.api.resources(
        type="upload",
        prefix=f"publr/{current_user.id}/",
        max_results=100,
    )
    urls = [r["secure_url"] for r in result["resources"]]
    return {"photos": urls}
