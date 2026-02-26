import json
import os

STATE_FILE = "processed.json"

def load_processed() -> set:
    if not os.path.exists(STATE_FILE):
        return set()
    with open(STATE_FILE) as f:
        return set(json.load(f))

def save_processed(processed: set):
    with open(STATE_FILE, "w") as f:
        json.dump(list(processed), f)