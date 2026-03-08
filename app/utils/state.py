import json
import os

PROCESSED_FILE = "processed.json"
FAILED_FILE = "failed.json"

def load_processed():
    if not os.path.exists(PROCESSED_FILE):
        return set()
    with open(PROCESSED_FILE) as file:
        return set(json.load(file))

def save_processed(processed):
    with open(PROCESSED_FILE, "w") as file:
        json.dump(list(processed), file)

def load_failed():
    if not os.path.exists(FAILED_FILE):
        return {}
    with open(FAILED_FILE) as file:
        return json.load(file)

def save_failed(failed):
    with open(FAILED_FILE, "w") as file:
        json.dump(failed, file)