import io
import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from app.publishers.cloudinarry import upload_image
from app.utils.state import load_processed, save_processed
from apscheduler.schedulers.asyncio import AsyncIOScheduler


DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def get_drive_client():
    creds = service_account.Credentials.from_service_account_info(
        json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    )

    return build("drive", "v3", credentials= creds)

async def check_drive():
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
        
        url = upload_image(path)
        print(f"uploaded to cloudinary: {url}")

        processed.add(file["id"])
        save_processed(processed)
        print(f"saved {file['name']} to {path}")


def start_watcher():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_drive, "interval", seconds=10)
    scheduler.start()
    print("driver watch started")