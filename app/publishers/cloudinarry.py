import os
import cloudinary
import cloudinary.uploader


def upload_image(file_path):
    cloudinary.config(
        cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
        api_key=os.environ["CLOUDINARY_API_KEY"],
        api_secret=os.environ["CLOUDINARY_API_SECRET"],
    )
    result = cloudinary.uploader.upload(file_path, folder="publr")
    return result["secure_url"]