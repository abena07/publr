import io
import os
import time
import uuid
from typing import Optional

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from PIL import Image
from pillow_heif import register_heif_opener
from sqlalchemy import select

from app.db.base import AsyncSessionLocal
from app.db.models import User
from app.publishers.cloudinary import upload_image
from app.publishers.instagram import publish_to_instagram
from app.utils.state import load_processed, save_processed, save_failed

register_heif_opener()


DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
MAX_SIZE = 1080

GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
TOKEN_URL = "https://oauth2.googleapis.com/token"


def get_drive_client(credentials: dict):
    creds = Credentials(token=credentials["access_token"])
    return build("drive", "v3", credentials=creds)


async def get_fresh_credentials(user_id: uuid.UUID) -> Optional[dict]:
    """Returns fresh credentials for a user, refreshing the access token if expired."""
    async with AsyncSessionLocal() as session:
        user = await session.get(User, user_id)
        if (
            not user
            or not user.google_access_token
            or not user.gdrive_folder_id
            or not user.instagram_user_id
            or not user.instagram_access_token
        ):
            return None

        if user.google_token_expires_at and time.time() > user.google_token_expires_at - 60:
            if not user.google_refresh_token:
                print(f"no refresh token for user {user_id}, skipping")
                return None
            async with httpx.AsyncClient() as client:
                resp = await client.post(TOKEN_URL, data={
                    "grant_type": "refresh_token",
                    "refresh_token": user.google_refresh_token,
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                })
                data = resp.json()
            if "error" in data:
                print(f"token refresh failed for user {user_id}: {data}")
                return None
            user.google_access_token = data["access_token"]
            user.google_token_expires_at = int(time.time()) + data.get("expires_in", 3600)
            await session.commit()

        return {
            "user_id": user.id,
            "access_token": user.google_access_token,
            "folder_id": user.gdrive_folder_id,
            "instagram_user_id": user.instagram_user_id,
            "instagram_access_token": user.instagram_access_token,
        }


def pad_to_valid_ratio(img):
    width, height = img.size
    ratio = width / height
    if ratio < 0.8:
        # too tall — pad width to match 4:5
        new_width = int(height * 0.8)
        padded = Image.new("RGB", (new_width, height), (0, 0, 0))
        padded.paste(img, ((new_width - width) // 2, 0))
        return padded
    elif ratio > 1.91:
        # too wide — pad height to match 1.91:1
        new_height = int(width / 1.91)
        padded = Image.new("RGB", (width, new_height), (0, 0, 0))
        padded.paste(img, (0, (new_height - height) // 2))
        return padded
    return img

def resize_image(path):
    img = Image.open(path).convert("RGB")
    img.thumbnail((MAX_SIZE, MAX_SIZE), Image.LANCZOS)
    img = pad_to_valid_ratio(img)
    img.save(path, "JPEG", quality=90)
    print(f"Resized image to max {MAX_SIZE}px : {path}")
    return path



async def check_drive(credentials: dict, session):
    user_id = credentials["user_id"]
    folder_id = credentials["folder_id"]
    drive = get_drive_client(credentials)

    results = drive.files().list(
        q=f"'{folder_id}' in parents and mimeType contains 'image/' and trashed =false",
        fields="files(id, name, mimeType)"
    ).execute()

    files = results.get("files", [])
    print(f"found {len(files)} image(s) in folder")
    processed = await load_processed(user_id, session)

    new_files = [f for f in files if f["id"] not in processed]

    for file in new_files:
        print(f"downloading {file['name']}")
        request = drive.files().get_media(fileId=file["id"])
        path = os.path.join(DOWNLOAD_DIR, file["name"])

        with io.FileIO(path, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

        try:
            resize_image(path)
        except Exception as e:
            print(f"resize failed for {file['name']}: {e}")
            continue

        try:
            url = upload_image(path)
            print(f"uploaded to cloudinary: {url}")
        except Exception as e:
            print(f"cloudinary upload failed for {file['name']}: {e}")
            continue

        ig_success = False
        try:
            caption = file.get("description", "")
            ig_success = await publish_to_instagram(
                url,
                user_id=credentials["instagram_user_id"],
                token=credentials["instagram_access_token"],
                caption=caption,
            )
            print(f"published to the gram successfully! : {url}")
        except Exception as e:
            print(f"publishing to instagram failed for {file['name']}: {e}")
            await save_failed(user_id, file["id"], url, session)

        try:
            os.remove(path)
            print(f"deleted temp file: {path}")
        except Exception as e:
            print(f"failed to deleted temp file: {path}-> {e}")

        if ig_success:
            await save_processed(user_id, file["id"], session)
            print(f"saved {file['name']} to processed")


async def poll_all_users():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.google_access_token.isnot(None),
                User.gdrive_folder_id.isnot(None),
            )
        )
        users = result.scalars().all()

    for user in users:
        credentials = await get_fresh_credentials(user.id)
        if credentials:
            async with AsyncSessionLocal() as session:
                await check_drive(credentials, session)


def start_watcher():
    interval_minutes = int(os.environ.get("POLL_INTERVAL_MINUTES", 5))
    scheduler = AsyncIOScheduler()
    scheduler.add_job(poll_all_users, "interval", minutes=interval_minutes)
    scheduler.start()
    print(f"drive watcher started — polling every {interval_minutes}m")
