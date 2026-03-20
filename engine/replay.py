import json
from pathlib import Path


def replay_build(target_dir):
    receipts_dir = Path(target_dir) / ".buildout_receipts"

    if not receipts_dir.exists():
        return {"status": "empty", "steps": 0}

    receipts = sorted(receipts_dir.glob("*.json"))

    replay_trace = []

    for r in receipts:
        data = json.loads(r.read_text())

        replay_trace.append({
            "phase": data["phase"],
            "hash": data["receipt_hash"],
            "parent": data.get("parent_hash"),
            "score": data.get("variant_score"),
        })

    return {
        "status": "ok",
        "steps": len(replay_trace),
        "trace": replay_trace,
    }
