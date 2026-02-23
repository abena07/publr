from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="publr")


@app.get("/health")
def health():
    return {"status": "ok"}
