import json, time, uuid
from pathlib import Path

LOG_PATH = Path("logs/telemetry.jsonl")
LOG_PATH.parent.mkdir(exist_ok=True)

SESSION_ID = str(uuid.uuid4())

def log_event(event_name, meta=None):
    record = {
        "session": SESSION_ID,
        "event": event_name,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "meta": meta or {}
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")