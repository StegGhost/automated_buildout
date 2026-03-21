import json
from pathlib import Path


def load_run_receipts(target_dir: str, run_id: str):
    run_dir = Path(target_dir) / ".buildout_runs" / run_id

    if not run_dir.exists():
        return []

    receipts = []

    for file in run_dir.glob("*.json"):
        with file.open() as f:
            receipts.append(json.load(f))

    receipts.sort(key=lambda x: x.get("timestamp", 0))
    return receipts
