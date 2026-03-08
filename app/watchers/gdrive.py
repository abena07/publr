import io
import json
import os
from PIL import Image
from pillow_heif import register_heif_opener
register_heif_opener()
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from app.publishers.cloudinary import upload_image
from app.publishers.instagram import publish_to_instagram
from app.utils.state import load_processed, save_processed, load_failed, save_failed
from apscheduler.schedulers.asyncio import AsyncIOScheduler


DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
MAX_SIZE = 1080

def get_drive_client():
    creds = service_account.Credentials.from_service_account_info(
        json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    )

    return build("drive", "v3", credentials= creds)

def resize_image(path):
    img = Image.open(path).convert("RGB")
    img.thumbnail((MAX_SIZE, MAX_SIZE), Image.LANCZOS)
    img.save(path, "JPEG", quality=90)
    print(f"Resized image to max {MAX_SIZE}px : {path}")
    return path


async def retry_failed():
    failed = load_failed()
    if not failed:
        return
    processed = load_processed()
    print(f"retrying {len(failed)} failed instagram publish(es)")
    for file_id, url in list(failed.items()):
        try:
            await publish_to_instagram(url)
            print(f"retry succeeded: {url}")
            del failed[file_id]
            save_failed(failed)
            processed.add(file_id)
            save_processed(processed)
        except Exception as e:
            print(f"retry failed for {url}: {e}")


async def check_drive():
    await retry_failed()
    folder_id = os.environ["GDRIVE_FOLDER_ID"]
    drive = get_drive_client()

    results = drive.files().list(
        q=f"'{folder_id}' in parents and mimeType contains 'image/' and trashed =false",
        fields="files(id, name, mimeType)"
    ).execute()

    files = results.get("files", [])
    print(f"found {len(files)} image(s) in folder")
    processed = load_processed()

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

        ig_success = False
        try:
            caption = file.get("description", "")
            ig_success = await publish_to_instagram(url, caption=caption)
            print(f"published to the gram successfully! : {url}")
        except Exception as e:
            print(f"publishing to instagram failed for {file['name']}: {e}")
            failed = load_failed()
            failed[file["id"]] = url
            save_failed(failed)

        try:
            os.remove(path)
            print(f"deleted temp file: {path}")
        except Exception as e:
            print(f"failed to deleted temp file: {path}-> {e}")

        if ig_success:
            processed.add(file["id"])
            save_processed(processed)
            print(f"saved {file['name']} to {path}")


def start_watcher():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_drive, "interval", seconds=10)
    scheduler.start()
    print("driver watch started")