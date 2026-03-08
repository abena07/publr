import json
import os

STATE_FILE = "processed.json"
FAILED_FILE = "failed.json"

def load_processed() -> set:
    if not os.path.exists(STATE_FILE):
        return set()
    with open(STATE_FILE) as f:
        return set(json.load(f))

def save_processed(processed: set):
    with open(STATE_FILE, "w") as f:
        json.dump(list(processed), f)

def load_failed() -> dict:
    if not os.path.exists(FAILED_FILE):
        return {}
    with open(FAILED_FILE) as f:
        return json.load(f)

def save_failed(failed: dict):
    with open(FAILED_FILE, "w") as f:
        json.dump(failed, f)