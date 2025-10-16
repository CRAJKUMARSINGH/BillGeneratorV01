import json, time
from pathlib import Path
LOG_PATH = Path("logs/audit_trail.jsonl")
LOG_PATH.parent.mkdir(exist_ok=True)

def record_event(user, action, bill_id):
    entry = {
        "user": user,
        "action": action,
        "bill_id": bill_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")