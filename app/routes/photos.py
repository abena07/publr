

import os

import cloudinary
import cloudinary.api
from fastapi import APIRouter


router = APIRouter()

@router.get("/api/photos")
def get_photos():

    cloudinary.config(
        cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
        api_key=os.environ["CLOUDINARY_API_KEY"],
        api_secret=os.environ["CLOUDINARY_API_SECRET"],
    )

    result = cloudinary.api.resources(
        type="upload",
        prefix="publr/",
        max_results=100,
    )
    urls = [r["secure_url"] for r in result["resources"]]
    return {"photos": urls}