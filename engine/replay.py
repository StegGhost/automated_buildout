import json
from pathlib import Path


def load_run_receipts(target_dir: str, run_id: str):
    base = Path(target_dir) / ".buildout_receipts" / run_id

    if not base.exists():
        return []

    receipts = []

    for file in base.glob("*.json"):
        with file.open() as f:
            receipts.append(json.load(f))

    receipts.sort(key=lambda x: x.get("timestamp", 0))

    return receipts


def load_previous_run_receipts(target_dir: str, current_run_id: str):
    base = Path(target_dir) / ".buildout_receipts"

    if not base.exists():
        return []

    runs = sorted([p.name for p in base.iterdir() if p.is_dir()])

    if current_run_id not in runs:
        return []

    idx = runs.index(current_run_id)

    if idx == 0:
        return []

    prev_run = runs[idx - 1]

    return load_run_receipts(target_dir, prev_run)


def replay_build(receipts: list):
    if not receipts:
        return {"status": "empty"}

    for i in range(1, len(receipts)):
        prev = receipts[i - 1]
        curr = receipts[i]

        if curr.get("parent_hash") != prev.get("receipt_hash"):
            return {
                "status": "invalid",
                "reason": "chain_break",
                "index": i,
            }

    return {"status": "ok"}
