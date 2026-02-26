from fastapi import FastAPI
from dotenv import load_dotenv

from app.watchers.gdrive import start_watcher

load_dotenv()

app = FastAPI(title="publr")

@app.on_event("startup")
async def startup():
    start_watcher()

@app.get("/health")
def health():
    return {"status": "ok"}


