import os
import uuid
from typing import Optional

import cloudinary
import cloudinary.uploader


def upload_image(
    file_path: str,
    user_id: uuid.UUID,
    credentials: Optional[dict] = None,
) -> str:
    if credentials:
        cloudinary.config(
            cloud_name=credentials["cloud_name"],
            api_key=credentials["api_key"],
            api_secret=credentials["api_secret"],
        )
        folder = "publr"
    else:
        cloudinary.config(
            cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
            api_key=os.environ["CLOUDINARY_API_KEY"],
            api_secret=os.environ["CLOUDINARY_API_SECRET"],
        )
        folder = f"publr/{user_id}"

    result = cloudinary.uploader.upload(file_path, folder=folder)
    return result["secure_url"]


def make_instagram_url(original_url: str, w: int, h: int) -> str:
    return original_url.replace("/upload/", f"/upload/c_fill,w_{w},h_{h}/")
