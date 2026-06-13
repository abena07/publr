import io
import os
import time
import uuid
from typing import Optional

import httpx
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from PIL import Image
from pillow_heif import register_heif_opener
from sqlalchemy import select

from app.scheduler import scheduler
from app.db.base import AsyncSessionLocal
from app.db.models import User
from app.publishers.cloudinary import upload_image, make_instagram_url, delete_image
from app.publishers.instagram import publish_to_instagram, delete_from_instagram
from app.utils.state import (
    load_processed, save_processed, load_failed, save_failed, delete_failed,
    load_processed_records, delete_processed, set_instagram_media_id, get_failed_record,
)
from app.utils.encryption import decrypt

register_heif_opener()


DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

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
                scheduler.pause_job(f"gdrive_watcher_{user_id}")
                user.gdrive_connected = False
                await session.commit()
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
                # Only a revoked/expired refresh token (invalid_grant) is a
                # permanent failure that genuinely requires the user to re-auth.
                # Anything else (network blip, Google 5xx, Railway/provider
                # downtime) is transient — leave gdrive_connected untouched and
                # let the next poll retry, so an outage can't silently disconnect.
                if data.get("error") == "invalid_grant":
                    print(f"refresh token revoked for user {user_id}: {data}")
                    scheduler.pause_job(f"gdrive_watcher_{user_id}")
                    user.gdrive_connected = False
                    await session.commit()
                else:
                    print(f"transient token refresh error for user {user_id}, will retry: {data}")
                return None
            user.google_access_token = data["access_token"]
            user.google_token_expires_at = int(time.time()) + data.get("expires_in", 3600)
            await session.commit()

        cloudinary_creds = None
        if user.cloudinary_cloud_name and user.cloudinary_api_key and user.cloudinary_api_secret:
            cloudinary_creds = {
                "cloud_name": decrypt(user.cloudinary_cloud_name),
                "api_key": decrypt(user.cloudinary_api_key),
                "api_secret": decrypt(user.cloudinary_api_secret),
            }

        return {
            "user_id": user.id,
            "access_token": user.google_access_token,
            "folder_id": user.gdrive_folder_id,
            "instagram_user_id": user.instagram_user_id,
            "instagram_access_token": user.instagram_access_token,
            "cloudinary_creds": cloudinary_creds,
        }


INSTAGRAM_FORMATS = [
    (1080, 1350),  # portrait  4:5
    (1080, 1080),  # square    1:1
    (1080,  566),  # landscape 1.91:1
]


def get_instagram_target(path: str) -> tuple:
    with Image.open(path) as img:
        w, h = img.size
    ratio = w / h
    return min(INSTAGRAM_FORMATS, key=lambda t: abs((t[0] / t[1]) - ratio))


async def check_drive(credentials: dict, session):
    user_id = credentials["user_id"]
    folder_id = credentials["folder_id"]
    drive = get_drive_client(credentials)

    failed = await load_failed(user_id, session)
    for file_id, cloudinary_url in failed.items():
        try:
            await publish_to_instagram(
                cloudinary_url,
                user_id=credentials["instagram_user_id"],
                token=credentials["instagram_access_token"],
                caption="",
            )
            await delete_failed(user_id, file_id, session)
            print(f"retried and published {file_id} to instagram")
        except Exception as e:
            print(f"retry failed for {file_id}: {e}")

    files = []
    page_token = None
    while True:
        kwargs = {
            "q": f"'{folder_id}' in parents and mimeType contains 'image/' and trashed=false",
            "fields": "nextPageToken, files(id, name, mimeType)",
        }
        if page_token:
            kwargs["pageToken"] = page_token
        results = drive.files().list(**kwargs).execute()
        files.extend(results.get("files", []))
        page_token = results.get("nextPageToken")
        if not page_token:
            break

    print(f"found {len(files)} image(s) in folder")

    processed_records = await load_processed_records(user_id, session)
    processed = set(processed_records.keys())
    drive_file_ids = {f["id"] for f in files}

    for file_id in processed - drive_file_ids:
        record = processed_records[file_id]
        if record.instagram_media_id and credentials.get("instagram_access_token"):
            try:
                await delete_from_instagram(record.instagram_media_id, credentials["instagram_access_token"])
                print(f"deleted {file_id} from instagram")
            except Exception as e:
                print(f"instagram delete failed for {file_id}: {e}")
        if record.cloudinary_public_id:
            try:
                delete_image(record.cloudinary_public_id, credentials.get("cloudinary_creds"))
                print(f"deleted {file_id} from cloudinary")
            except Exception as e:
                print(f"cloudinary delete failed for {file_id}: {e}")
        await delete_processed(user_id, file_id, session)
        failed_record = await get_failed_record(user_id, file_id, session)
        if failed_record:
            if failed_record.cloudinary_public_id:
                try:
                    delete_image(failed_record.cloudinary_public_id, credentials.get("cloudinary_creds"))
                    print(f"deleted failed file {file_id} from cloudinary")
                except Exception as e:
                    print(f"cloudinary delete (failed file) failed for {file_id}: {e}")
            await delete_failed(user_id, file_id, session)

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
            target_w, target_h = get_instagram_target(path)
        except Exception as e:
            print(f"failed to determine instagram format for {file['name']}: {e}")
            continue

        try:
            upload_result = upload_image(path, user_id=user_id, credentials=credentials.get("cloudinary_creds"))
            original_url = upload_result["secure_url"]
            cloudinary_public_id = upload_result["public_id"]
            print(f"uploaded to cloudinary: {original_url}")
        except Exception as e:
            print(f"cloudinary upload failed for {file['name']}: {e}")
            continue

        url = make_instagram_url(original_url, target_w, target_h)

        await save_processed(user_id, file["id"], session, cloudinary_public_id=cloudinary_public_id)
        print(f"saved {file['name']} to processed")

        try:
            caption = file.get("description", "")
            media_id = await publish_to_instagram(
                url,
                user_id=credentials["instagram_user_id"],
                token=credentials["instagram_access_token"],
                caption=caption,
            )
            await set_instagram_media_id(user_id, file["id"], media_id, session)
            print(f"published to the gram successfully! : {url}")
        except Exception as e:
            print(f"publishing to instagram failed for {file['name']}: {e}")
            await save_failed(user_id, file["id"], url, session, cloudinary_public_id=cloudinary_public_id)

        try:
            os.remove(path)
            print(f"deleted temp file: {path}")
        except Exception as e:
            print(f"failed to deleted temp file: {path}-> {e}")


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


async def poll_user(user_id):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            return

        credentials = await get_fresh_credentials(user.id)
        if credentials:
            await check_drive(credentials, session)


def start_watcher(user_id):
    interval_seconds = int(os.environ.get("WATCHER_INTERVAL_SECONDS", 60))
    scheduler.add_job(poll_user, "interval", seconds=interval_seconds, id=f"gdrive_watcher_{user_id}", args=[user_id])
    print(f"watcher started for user {user_id} — polling every {interval_seconds}s")
