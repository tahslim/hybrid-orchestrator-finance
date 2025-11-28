import json
from datetime import datetime

def log_result(path: str, obj: dict):
    t = datetime.utcnow().isoformat()
    with open(path, "a") as f:
        f.write(json.dumps({"ts": t, **obj}) + "\n")
