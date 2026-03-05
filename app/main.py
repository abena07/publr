from fastapi import FastAPI
from dotenv import load_dotenv

from app.watchers.gdrive import start_watcher
from app.routes.photos import router as photos_router

load_dotenv()

app = FastAPI(title="publr")



@app.on_event("startup")
async def startup():
    start_watcher()

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(photos_router)


