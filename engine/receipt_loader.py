import json
from pathlib import Path


def load_existing_receipts(target_dir: str):
    receipts_dir = Path(target_dir) / ".buildout_receipts"

    if not receipts_dir.exists():
        return []

    receipts = []

    for file in receipts_dir.glob("*.json"):
        try:
            with file.open() as f:
                data = json.load(f)

                # 🔥 skip incomplete receipts
                if "receipt_hash" not in data:
                    continue

                receipts.append(data)

        except Exception:
            # 🔥 skip corrupted/partial files
            continue

    # sort by timestamp
    receipts.sort(key=lambda x: x.get("timestamp", 0))

    # 🔥 ONLY keep latest run (strict isolation)
    latest = []
    current_ts = None

    for r in receipts:
        ts = int(r.get("timestamp", 0))

        if current_ts is None:
            current_ts = ts

        if ts == current_ts:
            latest.append(r)
        elif ts > current_ts:
            latest = [r]
            current_ts = ts

    return latest
